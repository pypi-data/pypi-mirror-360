# 小红书自动发稿脚本
# 该脚本使用Selenium WebDriver自动化发布图文和视频到小红书平台

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import json
import os
import win32clipboard  # 用于操作剪贴板，支持emoji字符（用pip install pywin32先安装主模块）


class XiaohongshuPoster:
    def __init__(self, path=os.path.dirname(os.path.abspath(__file__))):
        """
        初始化小红书发布器
        :param path: 当前执行文件所在目录
        """
        # 初始化WebDriver，这里使用Chrome浏览器
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)  # 设置等待超时时间为10秒
        
        # 获取当前执行文件所在目录
        current_dir = path
        
        # 定义token和cookies文件的路径
        self.token_file = os.path.join(current_dir, "xiaohongshu_token.json")
        self.cookies_file = os.path.join(current_dir, "xiaohongshu_cookies.json")
        
        # 加载token和cookies
        self.token = self._load_token()
        self._load_cookies()

    def _load_token(self):
        """
        从文件加载token
        :return: 返回加载的token，如果token过期或不存在则返回None
        """
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                    # 检查token是否过期
                    if token_data.get('expire_time', 0) > time.time():
                        return token_data.get('token')
            except:
                pass
        return None

    def _save_token(self, token):
        """
        保存token到文件
        :param token: 要保存的token
        """
        token_data = {
            'token': token,
            # token有效期设为30天
            'expire_time': time.time() + 30 * 24 * 3600
        }
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)

    def _load_cookies(self):
        """
        从文件加载cookies并添加到WebDriver
        """
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                self.driver.get("https://creator.xiaohongshu.com")
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            except:
                pass

    def _save_cookies(self):
        """
        保存WebDriver中的cookies到文件
        """
        cookies = self.driver.get_cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)

    def login_to_publish(self, title, content, images=None, slow_mode=False):
        """
        登录小红书并发布图文
        :param title: 文章标题
        :param content: 文章内容
        :param images: 图片路径列表
        :param slow_mode: 是否慢速模式，用于调试
        :return: 发布结果，成功返回True和"发布成功"，失败返回False和错误信息
        """
        self._load_cookies()
        self.driver.refresh()
        self.driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
        time.sleep(10)
        if self.driver.current_url != "https://creator.xiaohongshu.com/publish/publish?from=menu":
            return False, "登录失败"

        # 切换到上传图文标签
        tabs = self.driver.find_elements(By.CSS_SELECTOR, ".creator-tab")
        if len(tabs) > 1:
            tabs[2].click()  # 假设第3个标签是上传图文
            time.sleep(3)

        # 上传图片
        if images:
            upload_input = self.driver.find_element(By.CSS_SELECTOR, ".upload-input")
            upload_input.send_keys('\n'.join(images))  # 将所有图片路径用\n连接成一个字符串一次性上传
            time.sleep(1)

        # 通过剪贴板操作标题，达到支持emoji字符的目的
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, title[:20])  # 截取前20个字符作为标题
        finally:
            win32clipboard.CloseClipboard()

        # 写入标题
        title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".d-text")))
        title_input.send_keys(Keys.CONTROL, 'v')  # 对元素执行 Ctrl + V 的组合键操作

        # 通过剪贴板操作内容，达到支持emoji字符的目的
        try:
            win32clipboard.OpenClipboard()
            result = content.split("#")[0].rstrip()  # 取#前的内容并去除尾部空格
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, result)
        finally:
            win32clipboard.CloseClipboard()

        # 写入正文
        time.sleep(1)
        content_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor")))
        content_input.send_keys(Keys.CONTROL, 'v')  # 对元素执行 Ctrl + V 的组合键操作

        zt_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".contentBtn")))
        # 滚动到元素位置
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", zt_btn)
        # 确保元素可交互（可选）
        
        for vv in content.split("#")[1:]:
            content_input.send_keys(" ")
            bq = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".contentBtn")))
            bq.click()
            content_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor")))
            content_input.send_keys(vv.rstrip())
            #先择标签或主题
            time.sleep(3)

            #选择第一个标签（主题）
            bq_btn = self.wait.until(EC.presence_of_element_located((By.ID, "quill-mention-item-0")))
            bq_btn.click()
            time.sleep(1)

        # 发布
        if slow_mode:
            time.sleep(5)
        time.sleep(2)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".publishBtn")
        submit_btn.click()
        #print('发布成功')
        time.sleep(2)
        return True, "发布成功"

    def login_to_publish_video(self, title, content, videos=None, slow_mode=False):
        """
        登录小红书并发布视频
        :param title: 视频标题
        :param content: 视频内容
        :param videos: 视频路径列表
        :param slow_mode: 是否慢速模式，用于调试
        :return: 发布结果，成功返回True和"发布成功"，失败返回False和错误信息
        """
        self._load_cookies()
        self.driver.refresh()
        self.driver.get("https://creator.xiaohongshu.com/publish/publish?from=menu")
        time.sleep(3)
        if self.driver.current_url != "https://creator.xiaohongshu.com/publish/publish?from=menu":
            return False, "登录失败"

        # 上传视频
        if videos:
            upload_input = self.driver.find_element(By.CSS_SELECTOR, ".upload-input")
            upload_input.send_keys('\n'.join(videos))  # 将所有视频路径用\n连接成一个字符串一次性上传
            time.sleep(1)

        # 输入标题和内容
        time.sleep(3)
        title = title[:20]  # 截取前20个字符作为标题
        title_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".d-text")))
        title_input.send_keys(title)
        content_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ql-editor")))
        content_input.send_keys(content)

        # 发布
        if slow_mode:
            time.sleep(5)
        time.sleep(2)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, ".publishBtn")
        submit_btn.click()
        #print('发布成功')
        time.sleep(2)
        return True, "发布到小红书"

    def login(self, phone, country_code="+86"):
        """
        登录小红书
        :param phone: 手机号
        :param country_code: 国家区号，默认为"+86"
        """
        # 如果token有效则直接返回
        if self.token:
            return

        # 尝试加载cookies进行登录
        self.driver.get("https://creator.xiaohongshu.com/login")
        self._load_cookies()
        self.driver.refresh()
        time.sleep(3)

        # 检查是否已经登录
        if self.driver.current_url != "https://creator.xiaohongshu.com/login":
            print("使用cookies登录成功")
            self.token = self._load_token()
            self._save_cookies()
            time.sleep(2)
            return
        else:
            # 清理无效的cookies
            self.driver.delete_all_cookies()
            print("无效的cookies，已清理")

            # 如果cookies登录失败，则进行手动登录
            self.driver.get("https://creator.xiaohongshu.com/login")
            # 等待登录页面加载完成
            time.sleep(5)

            # 点击国家区号输入框（可选）
            skip = True
            if not skip:
                country_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='请选择选项']")))
                country_input.click()
                time.sleep(30)

            # 输入手机号和国家区号
            try:
                # 这里简化处理，直接输入+86区号和手机号
                phone_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='手机号']")))
                phone_input.clear()
                phone_input.send_keys(phone)

                # 点击发送验证码按钮（这里简化了选择器的尝试过程）
                send_code_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".css-uyobdj")))
                send_code_btn.click()
            except Exception as e:
                print("输入手机号或发送验证码出错:", e)
                return

            # 输入验证码
            verification_code = input("请输入验证码: ")
            code_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='验证码']")))
            code_input.clear()
            code_input.send_keys(verification_code)

            # 点击登录按钮
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".beer-login-btn")))
            login_button.click()

            # 等待登录成功,获取token
            time.sleep(3)
            self._save_cookies()


    def close(self):
        """
        关闭浏览器
        """
        self.driver.quit()