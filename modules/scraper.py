# modules/scraper.py
import cloudscraper
import re
from lxml import html
import trafilatura

def extract_article_content(url):
    """
    Lấy nội dung bài viết và Infobox.
    Hỗ trợ cả Fandom (aside) và Wikipedia (table).
    """
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        response = scraper.get(url)
        
        if response.status_code != 200:
            return None, f"Lỗi HTTP {response.status_code}"
            
        downloaded = response.text
        
        # --- 1. TRÍCH XUẤT INFOBOX ---
        infobox_text = ""
        try:
            tree = html.fromstring(downloaded)
            
            # A. Thử kiểu Fandom (portable-infobox)
            infoboxes = tree.xpath('//aside[contains(@class, "portable-infobox")]')
            
            # B. Nếu không có, thử kiểu Wikipedia (table.infobox)
            if not infoboxes:
                infoboxes = tree.xpath('//table[contains(@class, "infobox")]')

            if infoboxes:
                ib = infoboxes[0]
                lines = []
                
                # --- XỬ LÝ CHO FANDOM ---
                if ib.tag == 'aside':
                    titles = ib.xpath('.//h2[contains(@class, "pi-title")]')
                    if titles:
                        t_text = titles[0].text_content().strip()
                        lines.append(f"## Hồ sơ: {t_text}")
                    
                    data_items = ib.xpath('.//div[contains(@class, "pi-data")]')
                    for item in data_items:
                        label_node = item.xpath('.//h3[contains(@class, "pi-data-label")]')
                        value_node = item.xpath('.//div[contains(@class, "pi-data-value")]')
                        if label_node and value_node:
                            label = label_node[0].text_content().strip()
                            val_elem = value_node[0]
                            for br in val_elem.xpath(".//br"):
                                br.tail = ", " + (br.tail or "")
                            value = val_elem.text_content().strip()
                            lines.append(f"**{label}**: {value}")

                # --- XỬ LÝ CHO WIKIPEDIA ---
                elif ib.tag == 'table':
                    captions = ib.xpath('.//caption | .//th[contains(@class, "infobox-above")]')
                    if captions:
                        t_text = captions[0].text_content().strip()
                        lines.append(f"## Hồ sơ: {t_text}")
                    else:
                        lines.append("## Hồ sơ nhân vật")

                    rows = ib.xpath('.//tr')
                    for row in rows:
                        th = row.xpath('.//th')
                        td = row.xpath('.//td')
                        
                        if th and td:
                            label = th[0].text_content().strip()
                            val_elem = td[0]
                            for br in val_elem.xpath(".//br"):
                                br.tail = ", " + (br.tail or "")
                            for li in val_elem.xpath(".//li"):
                                li.tail = ", " + (li.tail or "")
                            value = val_elem.text_content().strip()
                            value = re.sub(r'\s+,\s+', ', ', value).strip(', ')
                            
                            if label and value:
                                lines.append(f"**{label}**: {value}")
                        
                        elif th and not td:
                            header_text = th[0].text_content().strip()
                            if header_text:
                                lines.append(f"\n### {header_text}")

                if lines:
                    infobox_text = "\n".join(lines) + "\n\n---\n\n"
        except Exception:
            pass 
        
        # --- 2. TRÍCH XUẤT NỘI DUNG ---
        result = trafilatura.extract(
            downloaded, 
            include_formatting=True, 
            output_format='markdown',
            include_tables=True,    
            include_comments=False, 
            include_images=False,
            favor_precision=False   
        )
        
        if not result:
            return None, "Không lấy được nội dung main text"

        result = re.sub(r'\[.*?\]', '', result)

        page_title = ""
        try:
            tree = html.fromstring(downloaded)
            h1 = tree.xpath('//h1')
            if h1: page_title = h1[0].text_content().strip()
        except: pass

        final_content = result
        if page_title:
            clean_start = result[:200].replace('#', '').strip()
            if page_title not in clean_start:
                final_content = f"# {page_title}\n\n{final_content}"
        
        if infobox_text:
            split_lines = final_content.split('\n', 1)
            if split_lines[0].strip().startswith('# '):
                final_content = f"{split_lines[0]}\n\n{infobox_text}{split_lines[1] if len(split_lines)>1 else ''}"
            else:
                final_content = f"{infobox_text}{final_content}"

        return final_content, "OK"
    except Exception as e:
        return None, f"Lỗi CloudScraper: {str(e)}"