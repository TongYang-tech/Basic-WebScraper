from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import json
import math 
import os, zipfile
import requests

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set
        # 2. start recursive search by calling dfs_visit
        self.visited.clear()
        self.order.clear()
        self.dfs_visit(node)

    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        # 2. mark node as visited by adding it to the set
        # 3. add this node to the end of self.order
        # 4. get list of node's children with this: self.go(node)
        # 5. in a loop, call dfs_visit on each of the children
        if node in self.visited:
            return
        self.visited.add(node)
        self.order.append(node)
        children = self.go(node)
        
        for i in children:
            self.dfs_visit(i)
     
    def bfs_search(self, node):
        self.visited.clear()
        self.bfs_visit(node)
        
    def bfs_visit(self, node):
        todo = [node]
        self.visited.add(node)
        
        while len(todo) > 0:
            curr = todo.pop(0)
            self.order.append(curr)
            childlist = self.go(curr)
            
            for child in childlist:
                if child not in self.visited:
                    todo.append(child)
                    self.visited.add(child)
            
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df
        
    def go(self, node):
        children = []
        for child in self.df.loc[node].items():
            if child[1]:
                children.append(child[0])
        return children
    
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        self.value = ""
        
    def go(self, node):
        children = None
        with open(os.path.dirname(__file__) + "/file_nodes/" + node, encoding="utf8") as f:
            for txt in f:
                if ".txt" not in txt:
                    self.value += txt.strip()
                else:
                    children = txt.strip().split(",")
        return children
    
    def message(self):
        word = self.value
        return word

class WebSearcher(GraphSearcher):
    def __init__(self, driver=None):
        super().__init__()
        self.driver = driver
        self.data = []
        
    def go(self, url):  
        
        children = []
        b = self.driver
        b.get(url)  
        pagesource = b.page_source
        table = pd.read_html(pagesource)[0]
        self.data.append(table)

        elem1 = b.find_elements(by='tag name', value='a')
        for elem in elem1:
            attribute = elem.get_attribute('href')
            children.append(attribute)
        return children
    
    def table(self):
        return pd.concat(self.data, ignore_index=True)
    
def reveal_secrets(driver, url, travellog):
    reveal_secret_message = ""
    
    for word in travellog["clue"]:
        reveal_secret_message += str(word)
        
    driver.get(url)
    
    go_here = driver.find_element_by_id("attempt-button")
    password_box = driver.find_element_by_id("password")
    password_box.send_keys(reveal_secret_message)
    
    go_here.click()
    time.sleep(1)
    security_view = driver.find_element_by_id("securityBtn")
    security_view.click()
    time.sleep(1)
    
    target_image = driver.find_element_by_id("image")
    target_location = driver.find_element_by_id("location")
    target_response = requests.get(target_image.get_attribute("src"))
    
    with open("Current_Location.jpg", "wb") as file:
        file.write(target_response.content)

    return target_location.get_attribute("innerText")