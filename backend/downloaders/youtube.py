# from playwright.sync_api import sync_playwright
# from playwright_stealth import stealth_sync
# import time
# import random

# def extract_download_results(page):
#     try:
#         # Wait for results with a timeout
#         page.wait_for_selector("#sf_result .media-result", timeout=60000)
        
#         results = []
#         result_boxes = page.query_selector_all("#sf_result .media-result .result-box.video")
        
#         for box in result_boxes:
#             # Extract thumbnail
#             thumb_img = box.query_selector(".thumb-box a img")
#             thumbnail_url = thumb_img.get_attribute("src") if thumb_img else None
            
#             # Extract title and duration
#             title = box.query_selector(".info-box .meta .title")
#             title_text = title.inner_text() if title else "No title"
            
#             duration = box.query_selector(".info-box .meta .duration")
#             duration_text = duration.inner_text() if duration else "Unknown duration"
            
#             # Extract download links
#             links = []
#             link_elements = box.query_selector_all(".link-download")
            
#             for link in link_elements:
#                 links.append({
#                     "quality": link.get_attribute("data-quality"),
#                     "type": link.get_attribute("data-type"),
#                     "text": link.inner_text().strip(),
#                     "url": link.get_attribute("href"),
#                     "downloadable": "no-downloadable" not in link.get_attribute("class")
#                 })
            
#             results.append({
#                 "thumbnail": thumbnail_url,
#                 "title": title_text.strip(),
#                 "duration": duration_text.strip(),
#                 "downloads": links
#             })
        
#         return results
    
#     except Exception as e:
#         print(f"Error extracting results: {str(e)}")
#         return None

# def get_youtube_info(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=True,
#             args=[
#                 "--no-sandbox",
#                 "--disable-setuid-sandbox",
#                 "--disable-blink-features=AutomationControlled"
#             ]
            
#             )
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         )
#         page = context.new_page()
#         stealth_sync(page)
#         try:
#             # Enable stealth (basic version without playwright_stealth)
#             page.add_init_script("""
#                 delete navigator.__proto__.webdriver;
#                 delete window.__proto__.webdriver;
#                 Object.defineProperty(navigator, 'webdriver', { get: () => false });
#             """)
#             # Optional: block trackers/ads
#             def block_ads(route, request):
#                if any(x in request.url for x in ["ads", "track", "analytics"]):
#                    return route.abort()
#                return route.continue_()
   
#             page.route("**/*", block_ads)
#                # Navigate to the site
#             page.goto("https://en1.savefrom.net/", wait_until="domcontentloaded")
#             time.sleep(random.uniform(1, 3))
            
#             # Fill the form
#             page.fill("#sf_url", url)
#             time.sleep(random.uniform(1, 2))
            
#             # Click submit
#             page.click("#sf_submit")
#             time.sleep(random.uniform(2, 4))
            
#             # Extract results
#             results = extract_download_results(page)
            
#             return {
#                 "success": True,
#                 "results": results
#             }
            
#         except Exception as e:
#             print(f"Error during scraping: {str(e)}")
#             return {
#                 "success": False,
#                 "error": str(e)
#             }
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random

def get_youtube_info(url):
    # Minimal Chrome options for maximum compatibility
    options = uc.ChromeOptions()
    
    # Essential options only
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")  # Use standard headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Basic stealth options
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--test-type")
    options.add_argument("--disable-automation")
    
    # Simple prefs without experimental options
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0
    }
    
    try:
        options.add_experimental_option("prefs", prefs)
    except:
        pass  # Skip if not supported
    
    driver = None
    try:
        print("Initializing Chrome driver...")
        # Simple driver initialization
        driver = uc.Chrome(options=options)
        
        print("Removing automation indicators...")
        # Basic stealth scripts
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("delete navigator.__proto__.webdriver")
        except:
            pass  # Skip if execution fails
        
        # Set timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        print("Navigating to SaveFrom.net...")
        driver.get("https://en1.savefrom.net/")
        time.sleep(random.uniform(3, 5))
        
        print("Looking for input field...")
        # Find and fill input
        input_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "sf_url"))
        )
        input_box.clear()
        input_box.send_keys(url)
        time.sleep(random.uniform(1, 2))
        print(f"Entered URL: {url}")
        
        print("Clicking submit button...")
        # Find and click submit
        submit_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "sf_submit"))
        )
        submit_btn.click()
        time.sleep(random.uniform(8, 12))
        
        print("Waiting for results...")
        # Wait for results to load
        try:
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#sf_result"))
            )
        except TimeoutException:
            print("Timeout waiting for results, trying to extract anyway...")
        
        # Extract results with simple approach
        results = []
        
        # Try to find result containers
        try:
            result_containers = driver.find_elements(By.CSS_SELECTOR, "#sf_result .media-result")
            if not result_containers:
                result_containers = driver.find_elements(By.CSS_SELECTOR, ".media-result")
            if not result_containers:
                result_containers = driver.find_elements(By.CSS_SELECTOR, "#sf_result")
            
            print(f"Found {len(result_containers)} result containers")
            
            for container in result_containers:
                try:
                    # Extract basic info
                    title = "Unknown Title"
                    try:
                        title_elem = container.find_element(By.CSS_SELECTOR, ".title")
                        title = title_elem.text.strip()
                    except:
                        try:
                            title_elem = container.find_element(By.TAG_NAME, "h3")
                            title = title_elem.text.strip()
                        except:
                            pass
                    
                    duration = "Unknown Duration"
                    try:
                        duration_elem = container.find_element(By.CSS_SELECTOR, ".duration")
                        duration = duration_elem.text.strip()
                    except:
                        pass
                    
                    thumbnail = ""
                    try:
                        thumb_elem = container.find_element(By.TAG_NAME, "img")
                        thumbnail = thumb_elem.get_attribute("src") or ""
                    except:
                        pass
                    
                    # Extract download links
                    downloads = []
                    try:
                        # Look for download links
                        link_elements = container.find_elements(By.CSS_SELECTOR, "a[href*='http']")
                        
                        for link in link_elements[:10]:  # Limit to first 10 links
                            href = link.get_attribute("href")
                            text = link.text.strip()
                            
                            if href and text and len(text) > 0:
                                downloads.append({
                                    "text": text,
                                    "url": href,
                                    "quality": link.get_attribute("data-quality") or "Unknown",
                                    "type": link.get_attribute("data-type") or "Unknown"
                                })
                    except Exception as e:
                        print(f"Error extracting links: {e}")
                    
                    if title != "Unknown Title" or downloads:
                        results.append({
                            "title": title,
                            "duration": duration,
                            "thumbnail": thumbnail,
                            "downloads": downloads
                        })
                        print(f"Extracted: {title} with {len(downloads)} download options")
                
                except Exception as e:
                    print(f"Error processing container: {e}")
                    continue
        
        except Exception as e:
            print(f"Error finding results: {e}")
            # Fallback: try to find any download links on the page
            try:
                all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='http']")
                download_links = []
                
                for link in all_links:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    
                    if href and text and any(word in text.lower() for word in ['download', 'mp4', 'mp3', 'video', 'audio']):
                        download_links.append({
                            "text": text,
                            "url": href,
                            "quality": "Unknown",
                            "type": "Unknown"
                        })
                
                if download_links:
                    results.append({
                        "title": "Video Download",
                        "duration": "Unknown",
                        "thumbnail": "",
                        "downloads": download_links[:5]  # Limit to 5
                    })
                    print(f"Fallback extraction found {len(download_links)} links")
            
            except Exception as fallback_error:
                print(f"Fallback extraction failed: {fallback_error}")
        
        print(f"Total results extracted: {len(results)}")
        
        return {
            "success": True,
            "results": results
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error during scraping: {error_msg}")
        
        # Save debug info
        if driver:
            try:
                driver.save_screenshot("error_debug.png")
                print("Debug screenshot saved as 'error_debug.png'")
                
                # Print page source snippet for debugging
                page_source = driver.page_source
                print(f"Page source length: {len(page_source)}")
                if "sf_result" in page_source:
                    print("Found sf_result in page source")
                else:
                    print("sf_result not found in page source")
                    
            except Exception as debug_error:
                print(f"Debug info collection failed: {debug_error}")
        
        return {
            "success": False,
            "error": error_msg
        }
        
    finally:
        if driver:
            try:
                driver.quit()
                print("Driver closed successfully")
            except:
                pass

