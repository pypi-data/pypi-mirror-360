#!/usr/bin/env python3
"""
一個 MCP 伺服器，提供統一的 網路搜尋 和 學術搜尋 的研究工具，
會追蹤相關連結，並將全面的資訊返回給 User。

此伺服器整合了 web_search 進行網路搜尋，以及 academic_search 進行學術內容搜尋
並將兩個來源的結果整合在一起，提供一個全面的研究結果。
並提供詳細的研究摘要和來源引用。


"""

import sys
import re
import logging
import os
from urllib.parse import quote_plus, unquote
from contextlib import asynccontextmanager

# 設定日誌記錄到 stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("deep-research")

# 嘗試匯入必要的相依套件
try:
    import httpx
    from bs4 import BeautifulSoup
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("正在安裝必要的相依套件...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "beautifulsoup4", "mcp"])
    import httpx
    from bs4 import BeautifulSoup
    from mcp.server.fastmcp import FastMCP

# 使用簡單的生命週期函式初始化伺服器
@asynccontextmanager
async def lifespan(app: FastMCP):
    """伺服器生命週期的內容管理器"""
    logger.info("伺服器正在啟動...")
    yield {}
    logger.info("伺服器正在關閉...")

# 初始化 MCP 伺服器
mcp = FastMCP(
    "deep-research",
    dependencies=["httpx", "beautifulsoup4"],
    lifespan=lifespan
)

# 設定
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# 從環境變數讀取設定，若未設定則使用預設值
try:
    MAX_CONTENT_SIZE = int(os.getenv("DEEP_RESEARCH_MAX_CONTENT_SIZE", "8096"))
except ValueError:
    logger.warning("DEEP_RESEARCH_MAX_CONTENT_SIZE 環境變數不是有效的整數，將使用預設值 8096")
    MAX_CONTENT_SIZE = 8096

try:
    MAX_RESULTS = int(os.getenv("DEEP_RESEARCH_MAX_RESULTS", "20"))
except ValueError:
    logger.warning("DEEP_RESEARCH_MAX_RESULTS 環境變數不是有效的整數，將使用預設值 20")
    MAX_RESULTS = 20

def safe_truncate(text, max_length, suffix="...\n[內容因長度限制已被截斷]"):
    """安全地將文字截斷至最大長度並加上後綴"""
    if not text or len(text) <= max_length:
        return text
    
    # 嘗試在段落邊界處截斷
    last_para_break = text[:max_length-50].rfind("\n\n")
    if last_para_break > max_length // 2:
        return text[:last_para_break] + "\n\n" + suffix
    
    return text[:max_length] + suffix

@mcp.tool()
async def deep_research(query: str, sources: str = "both", num_results: int = 20) -> str:
    """
    對一個主題進行全面的研究，並返回詳細資訊。

    Args:
        query: 研究問題或主題
        sources: 要使用的來源："web" 代表網頁資訊，"academic" 代表學術來源，"both" 代表所有來源
        num_results: 要檢查的來源數量 (預設為 20)

    Returns:
        結合多個來源的綜合研究結果
    """
    logger.info(f"開始研究：{query}，來源：{sources}，結果數量：{num_results}")
    
    # 驗證輸入
    if num_results > MAX_RESULTS:
        num_results = MAX_RESULTS
        
    sources = sources.lower().strip()
    if sources not in ["web", "academic", "both"]:
        sources = "both"
    
    try:
        # 從基本介紹開始
        result = f"研究查詢：{query}\n\n"
        source_text = "網路與學術來源" if sources == "both" else sources + " 來源"
        result += f"正在搜尋 {source_text}...\n\n"
        
        # 收集網路搜尋結果
        web_urls = []
        if sources in ["web", "both"]:
            try:
                web_results = await _web_search(query, num_results)
                result += "網路搜尋結果：\n" + web_results + "\n\n"
                web_urls = re.findall(r"URL: (https?://[^\s]+)", web_results)
                web_urls = web_urls[:num_results]
            except Exception as e:
                logger.error(f"網路搜尋錯誤：{str(e)}")
                result += f"網路搜尋錯誤：{str(e)[:100]}\n\n"
        
        # 收集學術搜尋結果
        academic_urls = []
        if sources in ["academic", "both"]:
            try:
                academic_results = await _academic_search(query, num_results)
                result += "學術搜尋結果：\n" + academic_results + "\n\n"
                academic_urls = re.findall(r"URL: (https?://[^\s]+)", academic_results)
                academic_urls = academic_urls[:num_results]
            except Exception as e:
                logger.error(f"學術搜尋錯誤：{str(e)}")
                result += f"學術搜尋錯誤：{str(e)[:100]}\n\n"
        
        # 檢查是否有找到任何結果
        if not web_urls and not academic_urls:
            return result + "找不到有效的研究結果。請嘗試不同的查詢。"
            
        # 合併 URL
        if sources == "both":
            combined_urls = []
            for i in range(max(len(web_urls), len(academic_urls))):
                if i < len(web_urls):
                    combined_urls.append(("web", web_urls[i]))
                if i < len(academic_urls):
                    combined_urls.append(("academic", academic_urls[i]))
            # 限制到請求的數量
            combined_urls = combined_urls[:num_results]
        elif sources == "web":
            combined_urls = [("web", url) for url in web_urls[:num_results]]
        else:  # 學術
            combined_urls = [("academic", url) for url in academic_urls[:num_results]]
        
        # 追蹤 URL 以獲取詳細內容
        result += f"來自前 {len(combined_urls)} 個來源的詳細內容：\n\n"
        
        for i, (source_type, url) in enumerate(combined_urls, 1):
            try:
                # 獲取內容
                page_content = await _follow_link(url)
                
                # 提取標題
                title_match = re.search(r"Title: (.+?)\n", page_content)
                title = title_match.group(1) if title_match else f"來源 {i}"
                
                # 新增到結果中
                separator = "=" * 40
                result += f"{separator}\n來源 {i} ({source_type})：{title}\n{separator}\n\n"
                result += page_content + "\n\n"
            except Exception as e:
                logger.error(f"追蹤 URL 時發生錯誤 {url}：{str(e)}")
                separator = "=" * 40
                result += f"{separator}\n來源 {i} ({source_type})：追蹤 URL 時發生錯誤\n{separator}\n"
                result += f"錯誤：{str(e)[:100]}\n\n"
        
        # 檢查大小並新增摘要
        # 為摘要保留空間
        summary = "\n研究摘要：\n"
        summary += f"已完成研究：{query}\n"
        source_summary = "網路與學術資料庫" if sources == "both" else sources + " 來源"
        summary += f"已檢查 {len(combined_urls)} 個來自 {source_summary} 的來源\n"
        summary += "以上資訊代表就此主題找到的最相關內容。\n"
        
        # 如有需要則進行截斷，以確保摘要符合大小限制
        max_size = MAX_CONTENT_SIZE - len(summary) - 50
        if len(result) > max_size:
            result = safe_truncate(result, max_size)

        # 新增摘要並返回
        result += summary
        logger.info(f"研究完成，返回 {len(result)} 個字元")
        return result
        
    except Exception as e:
        logger.error(f"deep_research 函式發生錯誤：{str(e)}")
        return f"研究錯誤：{str(e)[:200]}"

async def _web_search(query: str, num_results: int) -> str:
    """使用 DuckDuckGo 進行網路搜尋"""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            # 建立搜尋 URL
            encoded_query = quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # 設定標頭
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml"
            }
            
            # 發出請求
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # 解析結果
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = []
        
            # 提取結果
            result_blocks = soup.select(".result")
            for block in result_blocks:
                if len(search_results) >= num_results:
                    break
                    
                # 取得標題和 URL
                title_elem = block.select_one(".result__title a")
                if not title_elem:
                    continue
                    
                title = title_elem.get_text().strip()
                href = title_elem.get("href", "")
                
                # 從重新導向中提取實際 URL
                if "duckduckgo.com" in href:
                    url_match = re.search(r"uddg=([^&]+)", href)
                    if url_match:
                        href = unquote(url_match.group(1))
                
                # 取得摘要
                snippet_elem = block.select_one(".result__snippet")
                snippet = snippet_elem.get_text().strip() if snippet_elem else "沒有可用的摘要"
                
                # 新增至結果
                search_results.append({
                    "title": title[:100],
                    "url": href[:150],
                    "snippet": snippet[:200]
                })
            
            # 格式化結果
            results_text = f"網路搜尋結果：{query}\n\n"
            for i, result in enumerate(search_results, 1):
                results_text += f"{i}. {result['title']}\n"
                results_text += f"   URL: {result['url']}\n"
                results_text += f"   {result['snippet']}\n\n"
                
            return results_text if search_results else f"找不到關於「{query}」的網路搜尋結果"
                
    except Exception as e:
        logger.error(f"網路搜尋錯誤：{str(e)}")
        raise  # 重新引發錯誤，以便在主函式中處理

async def _academic_search(query: str, num_results: int) -> str:
    """使用 Semantic Scholar 進行學術搜尋"""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            # 建立搜尋 URL
            encoded_query = quote_plus(query)
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_query}&limit={num_results}&fields=title,url,year,authors,venue,abstract"
            
            # 發出請求
            headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return f"學術搜尋錯誤：API 返回狀態 {response.status_code}"
                
            # 解析結果
            json_data = response.json()
            results = json_data.get("data", [])
            
            if not results:
                return "找不到學術研究結果。請嘗試優化您的搜尋關鍵字。"
                
            # 處理結果
            search_results = []
            for paper in results:
                title = paper.get("title", "無標題論文")
                
                # 取得作者
                authors = paper.get("authors", [])
                author_names = [author.get("name", "") for author in authors if author.get("name")]
                author_names = author_names[:3]
                if len(authors) > 3:
                    author_names.append("et al.")
                author_text = ", ".join(author_names) if author_names else "作者不詳"
                
                # 取得出版資訊
                year = paper.get("year", "")
                venue = paper.get("venue", "")
                pub_info = f"{author_text} ({year})"
                if venue:
                    pub_info += f" - {venue}"
                    
                # 取得 URL 和摘要
                url = paper.get("url", "")
                abstract = paper.get("abstract", "沒有可用的摘要")
                
                search_results.append({
                    "title": title[:100],
                    "url": url[:150],
                    "authors_info": pub_info[:150],
                    "snippet": abstract[:200]
                })
                
            # 格式化結果
            results_text = f"學術搜尋結果：{query}\n\n"
            for i, result in enumerate(search_results, 1):
                results_text += f"{i}. {result['title']}\n"
                if result['url']:
                    results_text += f"   URL: {result['url']}\n"
                results_text += f"   {result['authors_info']}\n"
                results_text += f"   {result['snippet']}\n\n"
                
            return results_text
            
    except Exception as e:
        logger.error(f"學術搜尋錯誤：{str(e)}")
        raise  # 重新引發錯誤，以便在主函式中處理

async def _follow_link(url: str) -> str:
    """造訪一個 URL 並提取其內容"""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=8.0) as client:
            # 設定標頭
            headers = {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml"
            }
            
            # 發出請求
            response = await client.get(url, headers=headers)
            
            # 檢查內容類型
            content_type = response.headers.get("content-type", "").lower()
            if "application/pdf" in content_type:
                return f"標題：PDF 文件\nURL: {url}\n\n內容：[PDF 文件 - 無法直接提取內容]"
                
            # 解析 HTML
            soup = BeautifulSoup(response.text[:100000], "html.parser")  # 限制大小
            
            # 取得標題
            title = soup.title.string.strip() if soup.title and soup.title.string else "無標題"
            
            # 取得描述
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc and meta_desc.has_attr("content") else "沒有可用的描述"
            
            # 取得內容
            content_texts = []
            
            # 嘗試取得段落
            paragraphs = soup.find_all('p')
            for i, p in enumerate(paragraphs):
                if i >= 5:  # 限制為 5 個段落
                    break
                text = p.get_text().strip()
                if text and len(text) > 15:
                    content_texts.append(text[:300])
                    
            # 如果段落不足，嘗試其他元素
            if len(content_texts) < 2:
                elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
                for i, elem in enumerate(elements):
                    if i >= 8:
                        break
                    text = elem.get_text().strip()
                    if text and len(text) > 10:
                        content_texts.append(text[:200])
                        
            # 如果仍然沒有內容，使用我們能找到的任何文字
            if not content_texts:
                all_text = soup.get_text()
                clean_text = re.sub(r'\s+', ' ', all_text).strip()
                content_texts = [clean_text[:500]]
                
            # 格式化輸出
            content = "\n\n".join(content_texts)
            result = f"標題：{title[:100]}\nURL: {url}\n描述：{description[:200]}\n\n內容：\n{content}"
            
            return result
            
    except Exception as e:
        logger.error(f"追蹤連結時發生錯誤：{str(e)}")
        raise  # 重新引發錯誤，以便在主函式中處理

@mcp.prompt()
def deep_research(topic: str) -> str:
    """
    為一個主題建立全面、多階段的研究提示。

    Args:
        topic: 要研究的主題

    Returns:
        一個帶有 APA 引文格式的全面迭代研究提示
        並附上引用連結。
    """
    return (
        f"我需要對以下主題進行全面研究：{topic}\n\n"
        f"請遵循以下多步驟研究流程：\n\n"
        f"1. 初步探索：使用 deep_research 工具從網路和學術來源收集資訊。\n\n"
        f"2. 初步綜合：整理主要發現，識別核心概念、觀點和知識差距。 "
        f"為您的綜合報告建立一個產出項目以提高可讀性和組織性。包括方法論、 "
        f"主要發現和需要進一步調查的領域等部分。\n\n"
        f"3. 視覺化呈現：在適當情況下，建立數據視覺化圖表以說明研究中發現的關鍵概念、趨勢、 "
        f"或關係。可以考慮使用：\n"
        f"   - 時間軸圖表，用於呈現歷史發展\n"
        f"   - 比較表格，用於對比不同觀點\n"
        f"   - 概念圖，用於顯示想法之間的關係\n"
        f"   - 流程圖，用於說明過程\n"
        f"   - 長條圖/圓餅圖，用於呈現統計資訊\n"
        f"將這些視覺化圖表作為您分析產出項目的一部分呈現。\n\n"
        f"4. 後續研究：根據初步發現，確定 2-3 個需要更深入調查的特定方面。 "
        f"使用 deep_research 工具，透過更具體的查詢對這些方面進行有針對性的後續研究。\n\n"
        f"5. 全面綜合：將所有收集到的資訊整合成一個連貫的摘要，解釋要點、 "
        f"不同觀點以及對該主題的當前理解。突顯後續研究如何解決了 "
        f"知識差距或擴展了初步探索中的關鍵概念。建立一個最終的產出項目，包括：\n"
        f"   - 執行摘要\n"
        f"   - 方法論\n"
        f"   - 包含視覺化圖表的主要發現\n"
        f"   - 分析與詮釋\n"
        f"   - 結論與啟示\n\n"
        f"6. 參考文獻：在結尾處附上格式正確的 APA 第七版參考文獻列表。為您綜合報告中使用的每個來源建立 "
        f"適當的引文。當無法獲得確切的出版日期時，請使用可用的最佳資訊（例如網站 "
        f"版權日期，如果找不到日期則使用 'n.d.'）。網路來源的格式如下：\n"
        f"作者, A. A. (年, 月 日). 網頁標題. 網站名稱. URL\n\n"
        f"學術來源的格式如下：\n"
        f"作者, A. A., & 作者, B. B. (年). 文章標題. 期刊名稱, 卷號(期號), 頁碼範圍. DOI 或 URL\n\n"
        f"這種結合了適當引文和視覺元素的迭代方法，將整合來自多個權威來源的資訊，並以組織良好、視覺效果增強的格式呈現， "
        f"從而提供對 {topic} 的透徹理解。"
    )

def main():
    """主要執行函數，啟動 MCP 伺服器並處理致命錯誤"""
    try:
        logger.info("正在啟動 deep_research MCP 伺服器...")
        mcp.run()
    except Exception as e:
        logger.critical(f"致命錯誤：{str(e)}")
        sys.exit(1)

# 啟動伺服器
if __name__ == "__main__":
    main()