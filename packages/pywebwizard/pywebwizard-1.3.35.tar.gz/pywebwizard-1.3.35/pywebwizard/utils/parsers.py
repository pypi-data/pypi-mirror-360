from bs4 import BeautifulSoup
import re
import logging



def simplify_html(html_source: str) -> str:
    """
    Simplifica el HTML removiendo eventos JS y contenido del head excepto title.
    
    :param html_source: HTML source original
    :return: HTML simplificado
    """
    try:
        soup = BeautifulSoup(html_source, 'html.parser')
        
        head = soup.find('head')
        if head:
            title = head.find('title')
            title_text = title.get_text() if title else ""
            head.clear()
            if title_text:
                new_title = soup.new_tag('title')
                new_title.string = title_text
                head.append(new_title)
        
        js_events = [
            'onclick', 'onload', 'onunload', 'onchange', 'onsubmit', 'onreset',
            'onselect', 'onblur', 'onfocus', 'onkeydown', 'onkeypress', 'onkeyup',
            'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup',
            'ondblclick', 'onmouseenter', 'onmouseleave', 'onwheel', 'onscroll',
            'onresize', 'onerror', 'onabort', 'oncanplay', 'oncanplaythrough',
            'oncuechange', 'ondurationchange', 'onemptied', 'onended', 'oninput',
            'oninvalid', 'onloadeddata', 'onloadedmetadata', 'onloadstart',
            'onpause', 'onplay', 'onplaying', 'onprogress', 'onratechange',
            'onseeked', 'onseeking', 'onstalled', 'onsuspend', 'ontimeupdate',
            'onvolumechange', 'onwaiting', 'ontoggle', 'onshow', 'oncontextmenu',
            'oncopy', 'oncut', 'onpaste', 'ondrag', 'ondragend', 'ondragenter',
            'ondragleave', 'ondragover', 'ondragstart', 'ondrop', 'onhashchange',
            'onpageshow', 'onpagehide', 'onpopstate', 'onstorage', 'onbeforeunload',
            'onmessage', 'onoffline', 'ononline'
        ]
        
        for element in soup.find_all():
            for event in js_events:
                if element.has_attr(event):
                    del element[event]
        
        for script in soup.find_all('script'):
            script.decompose()
        
        for style in soup.find_all('style'):
            style.decompose()
        
        for element in soup.find_all():
            if element.has_attr('style'):
                style_content = element['style']
                if 'javascript:' in style_content.lower() or 'eval(' in style_content.lower():
                    element['style'] = re.sub(r'javascript:[^;]*;?', '', style_content, flags=re.IGNORECASE)
                    element['style'] = re.sub(r'eval\([^)]*\)', '', element['style'])
        
        for element in soup.find_all():
            if element.has_attr('href') and element['href'].lower().startswith('javascript:'):
                element['href'] = '#'
        
        for element in soup.find_all():
            if element.has_attr('src') and element['src'].lower().startswith('javascript:'):
                del element['src']
        
        return str(soup)
        
    except Exception as e:
        logging.error(f"[HTML] Error simplifying HTML: {str(e)}")
        return html_source
