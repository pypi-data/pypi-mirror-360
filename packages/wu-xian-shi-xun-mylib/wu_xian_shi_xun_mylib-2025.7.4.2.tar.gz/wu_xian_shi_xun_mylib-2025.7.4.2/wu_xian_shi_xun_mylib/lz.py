
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional

class CrossIframeFinder:
    def __init__(self, driver: WebDriver, implicit_wait_time: int = 3):
        """
        初始化 CrossIframeFinder 类。

        :param driver: WebDriver 实例。
        :param implicit_wait_time: 设置 WebDriver 的隐式等待时间。
        """
        self.driver = driver
        self.driver.implicitly_wait(implicit_wait_time)

    def find_element_cross_iframe(
        self,
        by: By,
        value: str,
        depth: int = 0,
        max_depth: int = 5
    ) -> Optional[WebElement]:
        """
        在多个 iframe 中跨框架查找元素。

        :param by: 用于定位元素的 By 枚举。
        :param value: 用于定位元素的值。
        :param depth: 当前递归的深度。
        :param max_depth: 递归搜索的最大深度。
        :return: 找到的 WebElement 或 None。
        """
        if depth >= max_depth:
            return None

        try:
            # 尝试在当前层级查找元素
            print(f"尝试在当前层级(depth={depth})查找元素: {by}='{value}'")
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            # 在当前层级未找到元素，继续在 iframes 中查找
            pass

        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")

        for index, iframe in enumerate(iframes):
            print(f"切换到第 {index} 个 iframe (depth={depth + 1})")
            self.driver.switch_to.frame(iframe)

            element = self.find_element_cross_iframe(by, value, depth=depth + 1, max_depth=max_depth)

            if element:
                print(f"在 iframe 中找到了元素: {by}='{value}'")
                return element

            print(f"在第 {index} 个 iframe 中未找到元素，返回上一层级")
            self.driver.switch_to.parent_frame()

        self.driver.switch_to.default_content()
        return None

