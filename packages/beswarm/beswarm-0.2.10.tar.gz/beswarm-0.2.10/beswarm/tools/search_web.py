import re
import os
import json
import httpx
import threading

from ..aient.src.aient.plugins import register_tool, get_url_content # Assuming a similar plugin structure

class ThreadWithReturnValue(threading.Thread):
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return

@register_tool()
async def search_web(query: str):
    """
获取 Google 搜索结果。

参数:
    query (str): 要在 Google 上搜索的查询字符串。

返回:
    dict: 包含搜索结果的字典，如果发生错误则包含错误信息。
    """
    api_key = os.environ.get('THORDATA_KEY')
    if not api_key:
        raise ValueError("THORDATA_KEY is not set in environment variables")

    api_url = "https://scraperapi.thordata.com/request"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # 请注意：硬编码的 API 密钥
    }
    payload = {
        "url": f"https://www.google.com/search?q={query}"
    }
    results = []

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()  # 如果状态码是 4xx 或 5xx，则引发 HTTPStatusError
            results = response.json()
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}",
            "status_code": e.response.status_code,
            "code": 400
        }
    except httpx.RequestError as e:
        return {
            "error": f"An error occurred while requesting {e.request.url!r}: {e}",
            "request_url": str(e.request.url),
            "code": 400
        }
    except json.JSONDecodeError:
        return {
            "error": "Failed to decode JSON response from the API.",
            "response_text": response.text if 'response' in locals() else "No response text available",
            "code": 400
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "code": 400
        }

    unique_urls = []
    if "error" in results or results.get("code", 200) != 200:
        # print(f"Error fetching search results for '{query}':")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        raise Exception(f"Error fetching search results for '{query}':")
    else:
        # print(f"Search results for '{query}':")
        html_content = results.get("data", {}).get("result", {}).get("html", "")
        if html_content:
            # 使用正则表达式查找所有 URL
            # 导入 html 和 urllib.parse 模块
            import html
            import urllib.parse

            # 1. 初步提取潜在的 URL 字符串
            #    使用更宽容的正则，允许末尾有非URL字符，后续清理
            candidate_urls = re.findall(r'https?://[^\s"]+|www\.[^\s"]+', html_content)

            processed_urls = []
            for url_str in candidate_urls:
                # 2. 解码十六进制表示 (例如 \x26 -> &)
                try:
                    def replace_hex(match):
                        return chr(int(match.group(1), 16))
                    url_str = re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, url_str)
                except ValueError:
                    pass

                # 3. 解码 HTML 实体 (例如 & -> &)
                url_str = html.unescape(url_str)

                # 4. 解码 URL 百分号编码 (例如 %3F -> ?, %3D -> =)
                url_str = urllib.parse.unquote(url_str)

                # 5. 精确截断已知的非 URL 参数或模式
                #    截断 ved= 参数
                if 'ved=' in url_str:
                    url_str = url_str.split('ved=', 1)[0]
                    url_str = url_str.rstrip('&?') # 移除可能残留的末尾 & 或 ?

                # 6. 迭代移除末尾的 HTML 标签
                #    例如 </cite>, <div...>, </span></span>
                old_url_len = -1
                while old_url_len != len(url_str): # 循环直到字符串不再变短
                    old_url_len = len(url_str)
                    # 移除末尾的完整闭合标签, e.g., </div>
                    url_str = re.sub(r'</[^>]+>$', '', url_str)
                    # 移除末尾的开始标签或不完整标签, e.g., <cite or <div
                    # (包括 < 开头到结尾的所有内容)
                    url_str = re.sub(r'<[^>]*$', '', url_str)
                    # 移除末尾的 > 单独字符，如果标签移除后残留
                    url_str = url_str.rstrip('>')


                # 7. 移除末尾的常见非URL字符 (引号，特定标点)
                #    注意顺序，这个应该在HTML标签移除后
                url_str = url_str.rstrip('\'";,.?!<>()[]{}') # '<' 也在这里再次检查

                # 8. 移除末尾单独的 '&' 字符 (在所有其他清理之后)
                url_str = url_str.rstrip('&')
                url_str = url_str.split("#:~:")[0]

                if url_str: #确保URL不为空
                    processed_urls.append(url_str)

            # 定义要过滤的域名列表
            excluded_domains = [
                "www.w3.org",
                "www.google.com",
                "ssl.gstatic.com",
                "translate.google.com",
                "www.googleadservices.com",
                "gstatic.com",
                "lens.google.com",
                "schema.org",
                "id.google.com",
                "maps.google.com",
                "clients6.google.com",
                "ogs.google.com",
                "policies.google.com",
                "support.google.com",
                "tpc.googlesyndication.com",
                "adssettings.google.com"
            ]

            final_urls_before_dedup = []
            for url in processed_urls:
                if not url:
                    continue
                if not any(excluded_domain in url for excluded_domain in excluded_domains):
                    # 9. 进一步规范化
                    # 9a. 移除末尾的 /
                    normalized_url = url.rstrip('/')

                    # 9b. 添加默认协议 (https) 如果缺失
                    if normalized_url and not normalized_url.startswith(('http://', 'https://')):
                        normalized_url = 'https://' + normalized_url

                    if normalized_url:
                         final_urls_before_dedup.append(normalized_url)

            # 10. 去重
            temp_unique_urls_set = set(final_urls_before_dedup)
            temp_unique_urls_set.discard("https://baike.baidu.com")
            temp_unique_urls_set.discard("https://zhuanlan.zhihu.com")
            unique_urls = sorted(list(temp_unique_urls_set))

    results = unique_urls
    if not results:
        return "No search results returned or results list is empty."

    web_contents_raw = []
    if results and isinstance(results, list) and len(results) > 0:
        # print(f"Fetching content for {len(results)} URLs...")
    # threads = []
    # for url in url_set_list:
    #     # url_search_thread = ThreadWithReturnValue(target=jina_ai_Web_crawler, args=(url,True,))
    #     url_search_thread = ThreadWithReturnValue(target=get_url_content, args=(url,))
    #     # url_search_thread = ThreadWithReturnValue(target=Web_crawler, args=(url,True,))
    #     url_search_thread.start()
    #     threads.append(url_search_thread)
        threads = []
        for i, link in enumerate(results):
            print(f"Processing URL {i + 1}/{len(results)}: {link}")
            # Assuming get_url_content is synchronous and returns a string or None
            # content_text = get_url_content(link)
            url_search_thread = ThreadWithReturnValue(target=get_url_content, args=(link,))
            url_search_thread.start()
            threads.append(url_search_thread)

        for thread in threads:
            content_text = thread.join()
            # content_text = thread.get_result()
            if content_text and len(content_text.split("\n\n")) > 10: # Ensure content_text is not None or empty before adding
                web_contents_raw.append({"url": link, "content": str(content_text)}) # Ensure content is string
            else:
                print(f"Warning: Failed to get content or content was empty for URL: {link}")
    elif not results or (isinstance(results, list) and len(results) == 0) :
        print("No search results returned or results list is empty.")
    else:
        print(f"Search results in unexpected format: {type(results)}")

    # print(f"Fetched {len(web_contents_raw)} web contents with text.")

    if not web_contents_raw:
        return "No web content"
    # if not web_contents_raw:
    #     print("No web content with text to process for similarity.")
    #     output_filename = "web_content_filtered.json"
    #     with open(output_filename, "w", encoding="utf-8") as f:
    #         json.dump([], f, indent=2, ensure_ascii=False)
    #     print(f"Empty list saved to {output_filename}")
    #     return

    # output_filename = "web_content.json"
    # with open(output_filename, "w", encoding="utf-8") as f:
    #     json.dump(web_contents_raw, f, indent=2, ensure_ascii=False)

    n = len(web_contents_raw)
    to_keep_flags = [True] * n  # Flags to mark which items to keep

    # print("Starting similarity comparison...")
    for i in range(n):
        if not to_keep_flags[i]:  # Skip if item i is already marked for discard
            continue

        content_i = web_contents_raw[i].get('content', "")
        if not isinstance(content_i, str):
            content_i = str(content_i) # Fallback, though str(content_text) above should handle it

        for j in range(i + 1, n):
            if not to_keep_flags[j]:  # Skip if item j is already marked for discard
                continue

            content_j = web_contents_raw[j].get('content', "")
            if not isinstance(content_j, str):
                content_j = str(content_j) # Fallback

            similarity = calculate_similarity(content_i, content_j)

            if similarity > 0.9:
                # print(f"Similarity > 0.9 ({similarity:.4f}) between content from '{web_contents_raw[i]['url']}' and '{web_contents_raw[j]['url']}'. Discarding the latter.")
                to_keep_flags[j] = False  # Discard the second item (item j)

    final_web_content = [web_contents_raw[i] for i in range(n) if to_keep_flags[i]]
    # print(f"Number of items after filtering: {len(final_web_content)}")

    # output_filename = "web_content_filtered.json"
    # with open(output_filename, "w", encoding="utf-8") as f:
    #     json.dump(final_web_content, f, indent=2, ensure_ascii=False)
    # print(f"Filtered web content saved to {output_filename}")
    final_result = ""
    for item in final_web_content:
        final_result += item["content"]
        final_result += "\n\n"
    if not final_result:
        return "No web content"
    return final_result

import difflib


def calculate_similarity(string1: str, string2: str) -> float:
    """Calculates the similarity ratio between two strings.

    Args:
        string1: The first string.
        string2: The second string.

    Returns:
        A float between 0 and 1, where 1 means the strings are identical
        and 0 means they are completely different.
    """
    return difflib.SequenceMatcher(None, string1, string2).ratio()

if __name__ == '__main__':
    import asyncio
    import re

    async def main():
        # 示例用法
        search_query = "美国"
        print(f"Performing web search for: '{search_query}'")
        results = await search_web(search_query)  # results is a list of URLs

        print(results)

    asyncio.run(main())

# python -m beswarm.tools.search_web
