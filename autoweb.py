# -*- coding=utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


class BasePageHandler:

    DONE = 0
    HANDLED = 1
    HANDLED_AND_CONTINUE = 2
    EXIT = 3

    def __init__(self):
        self.next = None
        self.debug = False

    def process(self, driver):  
        return self.DONE

    def highlight(self, driver, element):
        if element.is_displayed():
            driver.execute_script('arguments[0].style.outline="red solid thin"', element)

    def print_element(self, e):
        text = e.text
        text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        print('<{0}>{1}'.format(e.tag_name, text))

class CliHandler(BasePageHandler):

    def __init__(self):
        self.cmds = {
                'f' : self.cmd_find_element,
                'fs' : self.cmd_find_elements,
            }

    def cmd_find_element(self, dirver, x):
        by, arg = x.split(' ', 1)
        
        element = None
        if by == 'cl':
            element = dirver.find_element_by_class_name(arg)
        elif by == 'c':
            element = dirver.find_element_by_css_selector(arg)
        elif by == 'i':
            element = dirver.find_element_by_id(arg)
        elif by == 'l':
            element = dirver.find_element_by_link_text(arg)
        elif by == 'pl':
            element = dirver.find_element_by_partial_link_text(arg)
        elif by == 'n':
            element = dirver.find_element_by_name(arg)
        elif by == 't':
            element = dirver.find_element_by_tag_name(arg)
        elif by == 'x':
            element = dirver.find_element_by_xpath(arg)
        
        return element

    def cmd_find_elements(self, driver, x):
        by, arg = x.split(' ', 1)
        
        elements = None
        if by == 'cl':
            elements = driver.find_elements_by_class_name(arg)
        elif by == 'c':
            elements = driver.find_elements_by_css_selector(arg)
        elif by == 'i':
            elements = driver.find_elements_by_id(arg)
        elif by == 'l':
            elements = driver.find_elements_by_link_text(arg)
        elif by == 'pl':
            elements = driver.find_elements_by_partial_link_text(arg)
        elif by == 'n':
            elements = driver.find_elements_by_name(arg)
        elif by == 't':
            elements = driver.find_elements_by_tag_name(arg)
        elif by == 'x':
            elements = driver.find_elements_by_xpath(arg)
        
        return elements

    def process_cmds(self, driver, cmd_str):
        cmd, arg = cmd_str.split(' ', 1)

        if cmd in self.cmds:
            _ = self.cmds[cmd](driver, arg)
            if isinstance(_, list):
                for x in _:
                    self.print_element(x)
                    self.highlight(driver, x)
                print('count: {0}'.format(len(_)))
            elif _ is not None:
                self.print_element(_)
                self.highlight(driver, _)
        return _

    def process(self, driver):
        
        while True:
            
            try:
                cmd_str = input('>>>').strip(' ')

                if len(cmd_str) == 0:
                    continue
                elif cmd_str == 'exit':
                    return self.EXIT
                elif cmd_str == 'e':
                    break
                elif len(cmd_str) > 2:
                    _ = self.process_cmds(driver, cmd_str)
                else:
                    eval(cmd_str)
            except Exception as e:
                print(e)
            
        return self.HANDLED


class Order:

    UA_CHROME = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'

    def __init__(self, debug=False, debug_ex=False):
        self.handlers = []
        self.debug = debug
        self.debug_ex = debug_ex
        self.cli_handler = CliHandler()


    def init(self, user_agent=None, user_data_dir=None):

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        
        if user_agent is not None:
            options.add_argument('--user-agent={0}'.format(user_agent))
        if user_data_dir is not None:
            options.add_argument('--user-data-dir={0}'.format(user_data_dir)) 

        self.browser = webdriver.Chrome(chrome_options=options)

    
    def finalize(self):
        self.browser.close()
 
           
    def add_handler(self, handler):
        if isinstance(handler, list):
            for x in handler:
                self.handlers.append(x)
        else:
            self.handlers.append(handler)    
    
        
    def test(self):
        self.browser.find_element_by_link_text
        self.browser.find_element_by_id
        

    def run(self, url):
        
        handlers = self.handlers.copy()
        open_url = True

        while len(handlers) > 0:
            
            if open_url:
                self.browser.get(url)
                open_url = False

            handler = handlers[0]            
            if self.debug or handler.debug:
                if self.cli_handler.process(self.browser) == BasePageHandler.EXIT:
                    break

            try:
                state = handler.process(self.browser)
            except Exception as e:
                if not self.debug_ex:
                    print(e)
                    raise e
                # open the cmd line interface
                if self.cli_handler.process(self.browser) == BasePageHandler.EXIT:
                    break

            handlers.remove(handler)

            if state == BasePageHandler.DONE:
                break
            elif state == BasePageHandler.HANDLED:
                pass
            elif state == BasePageHandler.EXIT:
                break
                

class ScriptHandler(BasePageHandler):

    ACTION_CLICK = 'click'
    ACTION_MOVETO = 'moveto'
    ACTION_SENDKEYS = 'sendkeys'
    

    def __init__(self, element, action, arg=None, debug=False):
        self.element = element
        self.action = action
        self.arg = arg
        self.debug = debug

    def process(self, driver):
        print('[HANDLER]{0},{1},{2},{3}'.format(self.element, self.action, self.arg, self.debug))

        element = driver.find_element_by_xpath(self.element)
        ac = ActionChains(driver)

        if self.action == self.ACTION_CLICK:
            ac.click(element)
        elif self.action == self.ACTION_MOVETO:
            ac.move_to_element(element)
        elif self.action == self.ACTION_SENDKEYS:
            ac.send_keys_to_element(element, self.arg)

        ac.perform()

        return self.HANDLED


def parse_script(content):
    steps = []

    for x in content:
        
        fields = x.split('->') 
        fields = [f.strip(' ') for f in fields]
        
        element, action = fields[0], fields[1]
        arg = None
        debug = False

        if element.startswith('@'):
            element = element[1:]
            debug = True
        if action.startswith(ScriptHandler.ACTION_SENDKEYS):
            action, arg = action.split('#', 1)

        steps.append(ScriptHandler(element, action, arg, debug))
        
    return steps

if __name__ == '__main__':


    url = 'http://www.mi.com/index.html'

    o = Order(debug = False, debug_ex = True)
    o.init()

    script = [
        "@//a[text()='登录'] -> click",
        "//input[@name='user'] -> sendkeys#18938686780",
        "//input[@type='password'] -> sendkeys#whl229856331",
        "//input[@value='立即登录'] -> click",
        "//a[contains(text(),'路由器 智能硬件')] -> moveto",
        "//span[text()='手环及配件']/.. -> click",
        "//a[@href='//www.mi.com/shouhuan2/?cfrom=list'] -> click",
        "//a[text()='F码通道']/../../a -> click"
        ]
    
    handlers = parse_script(script)          
    o.add_handler(handlers)             

    try:
        o.run(url)
    except Exception as e:
        pass
    finally:
        o.finalize()