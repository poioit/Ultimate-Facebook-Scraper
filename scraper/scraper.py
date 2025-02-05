# -*- coding: utf-8 -*-
import json
import os
import sys
import urllib.request
import yaml
import utils
import argparse
import time
import locale
import inspect
from pyvirtualdisplay import Display
from sys import platform as _platform
from time import sleep
from datetime import datetime
import re
# for timezone
from pytz import timezone
from retry import retry

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
#import pyautogui
import storage
import requests
import time
import upload_s3 as s3

TELEGRAM_API_ROOT = 'https://api.telegram.org/'
apiURL = ''
debug_mode = 0
debug_post_id = 'groups/319005998759230/posts/506815109978317/'
query_db = 0
retry_list = []
ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET_ID = ''


def get_facebook_images_url(img_links):
    urls = []

    for link in img_links:
        if link != "None":
            valid_url_found = False
            driver.get(link)

            try:
                while not valid_url_found:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, selectors.get("spotlight"))
                        )
                    )
                    element = driver.find_element_by_class_name(
                        selectors.get("spotlight")
                    )
                    img_url = element.get_attribute("src")

                    if img_url.find(".gif") == -1:
                        valid_url_found = True
                        urls.append(img_url)
            except Exception:
                urls.append("None")
        else:
            urls.append("None")

    return urls


# -------------------------------------------------------------
# -------------------------------------------------------------

# takes a url and downloads image from that url
def image_downloader(img_links, folder_name):
    """
    Download images from a list of image urls.
    :param img_links:
    :param folder_name:
    :return: list of image names downloaded
    """
    img_names = []

    try:
        parent = os.getcwd()
        try:
            folder = os.path.join(os.getcwd(), folder_name)
            utils.create_folder(folder)
            os.chdir(folder)
        except Exception:
            print("Error in changing directory.")

        for link in img_links:
            img_name = "None"

            if link != "None":
                img_name = (link.split(".jpg")[0]).split("/")[-1] + ".jpg"

                # this is the image id when there's no profile pic
                if img_name == selectors.get("default_image"):
                    img_name = "None"
                else:
                    try:
                        urllib.request.urlretrieve(link, img_name)
                    except Exception:
                        img_name = "None"

            img_names.append(img_name)

        os.chdir(parent)
    except Exception:
        print("Exception (image_downloader):", sys.exc_info())
    return img_names


# -------------------------------------------------------------
# -------------------------------------------------------------


def extract_and_write_posts(elements, filename):
    try:
        f = open(filename, "w", newline="\r\n", encoding="utf-8")
        f.writelines(
            " TIME || TYPE  || TITLE || STATUS  ||   LINKS(Shared Posts/Shared Links etc) || POST_ID "
            + "\n"
            + "\n"
        )
        ids = []
        for x in elements:
            try:
                link = ""
                # id
                post_id = utils.get_post_id(x)
                ids.append(post_id)
                x.find_element_by_xpath(selectors.get("more_comment_replies"))
                # time
                time = utils.get_time(x)
                print(x.text)
                link, status, title, post_type = get_status_and_title(link, x)

                line = (
                    str(time)
                    + " || "
                    + str(post_type)
                    + " || "
                    + str(title)
                    + " || "
                    + str(status)
                    + " || "
                    + str(link)
                    + " || "
                    + str(post_id)
                    + "\n"
                )

                try:
                    print(line)
                    f.writelines(line.encode('utf-8'))
                except Exception:
                    print(sys.exc_info())
                    print("Posts: Could not map encoded characters")
            except Exception:
                pass
        f.close()
    except ValueError:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    except Exception:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    return


def extract_and_write_posts_onfan(elements, filename):
    try:
        f = open(filename, "w", newline="\r\n", encoding="utf-8")
        f.writelines(
            " TIME || TYPE  || TITLE || STATUS  ||   LINKS(Shared Posts/Shared Links etc) || POST_ID "
            + "\n"
            + "\n"
        )
        ids = []
        for x in elements:
            try:
                link = ""
                # id
                post_id = utils.get_post_id(x)
                print(post_id)
                ids.append(post_id)

                # locale.setlocale(locale.LC_ALL, 'zh_CN.utf-8')
                # latest_time = storage.rest_get_posts('luxurai_backend')
                # time
                time = utils.get_time(x)
                print(x.text)
                #link, status, title, post_type = get_fan_status_and_title(link, x)

                line = (
                    str(time)
                    + " || "
                    + str(post_type)
                    + " || "
                    + str(title)
                    + " || "
                    + str(status)
                    + " || "
                    + str(link)
                    + " || "
                    + str(post_id)
                    + "\n"
                )

                try:
                    print(line)
                    f.writelines(line.encode('utf-8'))
                except Exception:
                    print(sys.exc_info())
                    print("Posts: Could not map encoded characters")
            except Exception:
                pass
        f.close()
    except ValueError:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    except Exception:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    return


def get_fan_status_and_title(link, x):
    # title
    title = utils.get_title(x, selectors)
    if title.text.find("shared a memory") != -1:
        x = x.find_element_by_xpath(selectors.get("title_element"))
        title = utils.get_title(x, selectors)
    status = utils.get_status(x, selectors)
    try:
        # time.sleep(20)
        result = driver.find_element_by_xpath(
            selectors.get("title_text_fan")).text
        print(result)
        if title.text == result or result.index(title.text):
            if status == "":
                temp = utils.get_div_links(x, "img", selectors)
                if temp == "":  # no image tag which means . it is not a life event
                    link = utils.get_div_links(
                        x, "a", selectors).get_attribute("href")
                    post_type = "status update without text"
                else:
                    post_type = "life event"
                    link = utils.get_div_links(
                        x, "a", selectors).get_attribute("href")
                    status = utils.get_div_links(x, "a", selectors).text
            else:
                post_type = "status update"
                if utils.get_div_links(x, "a", selectors) != "":
                    link = utils.get_div_links(
                        x, "a", selectors).get_attribute("href")

        elif title.text.find(" shared ") != -1:
            x1, link = utils.get_title_links(title)
            post_type = "shared " + x1
        elif title.text.find(" at ") != -1 or title.text.find(" in ") != -1:
            if title.text.find(" at ") != -1:
                x1, link = utils.get_title_links(title)
                post_type = "check in"
            elif title.text.find(" in ") != 1:
                status = utils.get_div_links(x, "a", selectors).text
        elif title.text.find(" added ") != -1 and title.text.find("photo") != -1:
            post_type = "added photo"
            link = utils.get_div_links(x, "a", selectors).get_attribute("href")

        elif title.text.find(" added ") != -1 and title.text.find("video") != -1:
            post_type = "added video"
            link = utils.get_div_links(x, "a", selectors).get_attribute("href")

        else:
            post_type = "others"
        if not isinstance(title, str):
            title = title.text
        status = status.replace("\n", " ")
        title = title.replace("\n", " ")
    except NoSuchElementException:  # spelling error making this code not work as expected
        pass
    except Exception:
        print("Exception (get_fan_status_and_title)", "Status =", sys.exc_info())
    return link, status, title, post_type


def get_status_and_title(link, x):
    # title
    title = utils.get_title(x, selectors)
    if title.text.find("shared a memory") != -1:
        x = x.find_element_by_xpath(selectors.get("title_element"))
        title = utils.get_title(x, selectors)
    status = utils.get_status(x, selectors)
    try:
        if title.text == driver.find_element_by_id(selectors.get("title_text")).text:
            if status == "":
                temp = utils.get_div_links(x, "img", selectors)
                if temp == "":  # no image tag which means . it is not a life event
                    link = utils.get_div_links(
                        x, "a", selectors).get_attribute("href")
                    post_type = "status update without text"
                else:
                    post_type = "life event"
                    link = utils.get_div_links(
                        x, "a", selectors).get_attribute("href")
                    status = utils.get_div_links(x, "a", selectors).text
            else:
                post_type = "status update"
                if utils.get_div_links(x, "a", selectors) != "":
                    link = utils.get_div_links(
                        x, "a", selectors).get_attribute("href")

        elif title.text.find(" shared ") != -1:
            x1, link = utils.get_title_links(title)
            post_type = "shared " + x1
        elif title.text.find(" at ") != -1 or title.text.find(" in ") != -1:
            if title.text.find(" at ") != -1:
                x1, link = utils.get_title_links(title)
                post_type = "check in"
            elif title.text.find(" in ") != 1:
                status = utils.get_div_links(x, "a", selectors).text
        elif title.text.find(" added ") != -1 and title.text.find("photo") != -1:
            post_type = "added photo"
            link = utils.get_div_links(x, "a", selectors).get_attribute("href")

        elif title.text.find(" added ") != -1 and title.text.find("video") != -1:
            post_type = "added video"
            link = utils.get_div_links(x, "a", selectors).get_attribute("href")

        else:
            post_type = "others"
        if not isinstance(title, str):
            title = title.text
        status = status.replace("\n", " ")
        title = title.replace("\n", " ")
    except Exception:
        print("Exception (get_status_and_title)", "Status =", sys.exc_info())
    return link, status, title, post_type


def extract_and_write_group_posts(elements, filename):
    try:
        f = create_post_file(filename)
        ids = set()
        cnt = 0
        # query from database
        if query_db == 1:
            ids = storage.get_helpbuypost('')
            pass
        else:
            # query from web pages
            driver.find_element_by_tag_name(
                'body').send_keys(Keys.CONTROL + Keys.HOME)
            for x in elements:
                try:
                    # id
                    print(cnt)
                    cnt = cnt+1

                    try:
                        driver.execute_script(
                            "return arguments[0].scrollIntoView(true);", x)
                        sleep(0.1)
                        driver.execute_script("scrollBy(0,-1200);")
                        sleep(0.1)
                    except Exception:
                        pass

                    hov = ActionChains(driver)
                    hov.move_to_element(x).perform()
                    sleep(0.05)

                    # pyautogui.typewrite(['down','down','down','down','enter'])
                    # hov.move_to_element(x).click().perform()
                    # driver.back()
                    # hov.contextClick(x)
                    # hov.perform()
                    #post_id = x.get_attribute("role")
                    els = driver.find_elements_by_xpath(
                        selectors.get("group_id"))
                    for y in els:
                        try:

                            post_id = y.get_attribute("href")
                            # print(post_id)
                            regex = re.compile(
                                '\w+\/(groups\/\w+\/posts\/\d+\/).')

                            post_id = regex.findall(post_id)
                            if len(post_id):
                                ids.add(post_id[0])
                        except Exception as e:
                            print("clicke error" . str(e))
                            pass
                    #post_href = x.get_attribute("href")
                    # print(post_href)
                    #attrs = driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', x)
                    # print(attrs)
                except Exception as e:
                    print(e)
                    pass
            '''
            eles = driver.find_elements_by_xpath(selectors.get("group_id"))
            for x in eles:
                try:
                    post_id = utils.get_group_post_id(x)
                    ids.append(post_id)
                except Exception:
                    pass
            '''
        total = len(ids)
        i = 0
        j = 0
        retry_cnt = 0
        # locale.setlocale(locale.LC_ALL, 'zh_CN.utf-8')
        # latest is not precise, stop use it
        # latest_time = storage.get_posts('luxurai_backend')
        # print(latest_time)
        if debug_mode == 1:
            for post_id in ids:
                print(str(j) + ':' + post_id)
                j += 1
            try:
                add_group_post_to_file(
                    f, filename, debug_post_id, j, total, None, reload=True)
            except ValueError:
                pass
        else:
            for post_id in ids:
                #post_id = 'groups/raymond30/posts/369709753999151/'
                i += 1
                try:
                    add_group_post_to_file(
                        f, filename, post_id, i, total, None, reload=True)
                except ValueError:
                    pass
        print('doing retry list:')
        for post_id in retry_list:
            try:
                retry_cnt += 1
                add_group_post_to_file(f, filename, post_id, retry_cnt, len(
                    retry_list), None, reload=True)
            except ValueError:
                pass
        f.close()
    except ValueError:
        frame = inspect.currentframe()
        # __FILE__
        fileName = frame.f_code.co_filename
        # __LINE__
        fileNo = frame.f_lineno
        print(fileName + str(fileNo) +
              "Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    except Exception:
        frame = inspect.currentframe()
        # __FILE__
        fileName = frame.f_code.co_filename
        # __LINE__
        fileNo = frame.f_lineno
        print(fileName + str(fileNo) +
              "Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    return


def extract_and_write_fan_posts(elements, filename):
    try:
        f = create_post_file(filename)
        ids = []
        for x in elements:
            try:
                # id
                post_href = utils.get_fan_post_href(x)
                ids.append(post_href)
            except Exception:
                pass
        total = len(ids)
        i = 0
        locale.setlocale(locale.LC_ALL, 'zh_CN.utf-8')
        latest_time = storage.rest_get_posts('luxurai_backend')
        print(latest_time)

        for post_href in ids:
            i += 1
            try:
                add_group_post_to_file(
                    f, filename, post_href, i, total, latest_time, reload=False)
            except ValueError:
                print('value error')
                pass
        f.close()
    except ValueError:
        print("Exception (extract_and_write_fan_posts)",
              "Status =", sys.exc_info())
    except Exception:
        print("Exception (extract_and_write_fan_posts)",
              "Status =", sys.exc_info())
    return


def extract_and_write_group_members(elements, filename):
    try:
        f = create_post_file(filename)
        user_list = []
        current_url = driver.current_url
        regex = re.compile('.+\/groups\/(\w+)\/.+')
        group = regex.findall(current_url)[0]
        uploader = s3.S3uploader(ACCESS_KEY, SECRET_KEY, BUCKET_ID)
        for y in elements:
            try:
                #x = y.find_elements_by_xpath("../../../../..//div[@class='q9uorilb l9j0dhe7 pzggbiyp du4w35lb']/*[@class='pzggbiyp']/*")
                photolink = y.find_elements_by_xpath(
                    selectors.get("group_member_photo"))[0]
                urllink = y.find_elements_by_xpath(
                    selectors.get("group_member_link"))[0]
                user_profile = {}
                user_ref = urllink.get_attribute("href")
                regex = re.compile('.+\/(\d+)')
                user_id = regex.findall(user_ref)[0]
                print(user_id)
                user_profile['user_id'] = user_id
                user_profile['name'] = urllink.text
                user_profile['group_ids'] = [group]
                user_profile['photo'] = photolink.get_attribute("xlink:href")

                backup_photo = uploader.upload(user_profile['photo'], user_id)
                user_profile['backup_photo'] = backup_photo
                cur_user = storage.get_fbuser(user_id)
                if cur_user is not None and group not in cur_user['group_ids']:
                    cur_user['group_ids'].append(group)
                    user_profile = cur_user
                user_list.append(user_profile)
                # we still need to update the user photo
                # elif cur_user is not None:
                #    continue
                # remove here to update in the following process
                # if not cur_user:
                storage.update_user(user_profile)
            except Exception:
                pass
        total = len(user_list)
        print(total)
        groupurl = 'https://www.facebook.com/groups/' + group + '/user/'
        profile_page = [groupurl + user['user_id'] for user in user_list]
        for i, _ in enumerate(profile_page):
            try:
                cur_user = storage.get_fbuser(user_list[i]['user_id'])
                if (cur_user is not None) and (not 'join_groups' in cur_user or ('join_groups' in cur_user and not utils.contains(cur_user['join_groups'], lambda x: x['group_id'] == group))):
                    print(i)
                    driver.get(profile_page[i])
                    driver.implicitly_wait(60)
                    sleep(5)
                    user_added_date = driver.find_elements_by_xpath(
                        selectors.get("user_added_date")
                    )
                    for j, _ in enumerate(user_added_date):
                        if(hasattr(user_added_date[j], 'text')):
                            # print(user_added_date[j].text)
                            regex = re.compile('(\d+年.+月.+日).+')
                            added_date = regex.findall(user_added_date[j].text)
                            if len(added_date):
                                print(added_date[0])
                                join_date = datetime.strptime(
                                    added_date[0], "%Y年%m月%d日")
                                join_date = timezone(
                                    'Asia/Taipei').localize(join_date)
                                if not hasattr(user_list[i], 'join_groups'):
                                    user_list[i]['join_groups'] = []
                                else:
                                    user_list[i]['join_groups'] = cur_user['join_groups']
                                user_list[i]['join_groups'].append(
                                    {'group_id': group, 'join_date': join_date})

                                storage.update_user(user_list[i])
                                break
                    driver.get('https://www.facebook.com/groups/' +
                               group + '/members/')
                driver.implicitly_wait(60)
                sleep(5)
            except Exception:
                pass
        f.close()
    except ValueError:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    except Exception:
        print("Exception (extract_and_write_posts)", "Status =", sys.exc_info())
    return


def add_group_post_to_file(f, filename, post_id, number=1, total=1, latest_time=None, reload=False):
    print("Scraping Post(" + post_id + "). " +
          str(number) + " of " + str(total))
    photos_dir = os.path.dirname(filename)
    if reload:
        driver.get(utils.create_post_link(post_id, selectors))
    line = get_group_post_as_line(post_id, photos_dir, latest_time)
    print(line)
    try:
        f.writelines(line)
    except Exception:
        print(sys.exc_info())
        print("Posts: Could not map encoded characters")


def create_post_file(filename):
    """
    Creates post file and header
    :param filename:
    :return: file
    """
    f = open(filename, "w", newline="\r\n", encoding="utf-8")
    f.writelines(
        "TIME || TYPE  || TITLE || STATUS || LINKS(Shared Posts/Shared Links etc) || POST_ID || "
        "PHOTO || COMMENTS " + "\n"
    )
    return f


# -------------------------------------------------------------
# -------------------------------------------------------------


def save_to_file(name, elements, status, current_section):
    """helper function used to save links to files"""

    # status 0 = dealing with friends list
    # status 1 = dealing with photos
    # status 2 = dealing with videos
    # status 3 = dealing with about section
    # status 4 = dealing with posts
    # status 5 = dealing with group posts

    try:
        f = None  # file pointer

        if status != 4 and status != 5 and status != 6:
            f = open(name, "w", encoding="utf-8", newline="\r\n")

        results = []
        img_names = []

        # dealing with Friends
        if status == 0:
            # get profile links of friends
            results = [x.get_attribute("href") for x in elements]
            results = [create_original_link(x) for x in results]

            # get names of friends
            people_names = [
                x.find_element_by_tag_name("img").get_attribute("aria-label")
                for x in elements
            ]

            # download friends' photos
            try:
                if download_friends_photos:
                    if friends_small_size:
                        img_links = [
                            x.find_element_by_css_selector(
                                "img").get_attribute("src")
                            for x in elements
                        ]
                    else:
                        links = []
                        for friend in results:
                            try:
                                driver.get(friend)
                                WebDriverWait(driver, 30).until(
                                    EC.presence_of_element_located(
                                        (
                                            By.CLASS_NAME,
                                            selectors.get("profilePicThumb"),
                                        )
                                    )
                                )
                                l = driver.find_element_by_class_name(
                                    selectors.get("profilePicThumb")
                                ).get_attribute("href")
                            except Exception:
                                l = "None"

                            links.append(l)

                        for i, _ in enumerate(links):
                            if links[i] is None:
                                links[i] = "None"
                            elif links[i].find("picture/view") != -1:
                                links[i] = "None"

                        img_links = get_facebook_images_url(links)

                    folder_names = [
                        "Friend's Photos",
                        "Mutual Friends' Photos",
                        "Following's Photos",
                        "Follower's Photos",
                        "Work Friends Photos",
                        "College Friends Photos",
                        "Current City Friends Photos",
                        "Hometown Friends Photos",
                    ]
                    print("Downloading " + folder_names[current_section])

                    img_names = image_downloader(
                        img_links, folder_names[current_section]
                    )
                else:
                    img_names = ["None"] * len(results)
            except Exception:
                print(
                    "Exception (Images)",
                    str(status),
                    "Status =",
                    current_section,
                    sys.exc_info(),
                )

        # dealing with Photos
        elif status == 1:
            results = [x.get_attribute("href") for x in elements]
            results.pop(0)

            try:
                if download_uploaded_photos:
                    if photos_small_size:
                        background_img_links = driver.find_elements_by_xpath(
                            selectors.get("background_img_links")
                        )
                        background_img_links = [
                            x.get_attribute("style") for x in background_img_links
                        ]
                        background_img_links = [
                            ((x.split("(")[1]).split(")")[0]).strip('"')
                            for x in background_img_links
                        ]
                    else:
                        background_img_links = get_facebook_images_url(results)

                    folder_names = ["Uploaded Photos", "Tagged Photos"]
                    print("Downloading " + folder_names[current_section])

                    img_names = image_downloader(
                        background_img_links, folder_names[current_section]
                    )
                else:
                    img_names = ["None"] * len(results)
            except Exception:
                print(
                    "Exception (Images)",
                    str(status),
                    "Status =",
                    current_section,
                    sys.exc_info(),
                )

        # dealing with Videos
        elif status == 2:
            results = elements[0].find_elements_by_css_selector("li")
            results = [
                x.find_element_by_css_selector("a").get_attribute("href")
                for x in results
            ]

            try:
                if results[0][0] == "/":
                    results = [r.pop(0) for r in results]
                    results = [(selectors.get("fb_link") + x) for x in results]
            except Exception:
                pass

        # dealing with About Section
        elif status == 3:
            results = elements[0].text
            f.writelines(results)

        # dealing with Posts
        elif status == 4:
            extract_and_write_posts(elements, name)
            return

        # dealing with Group Posts
        elif status == 5:
            extract_and_write_group_posts(elements, name)
            return

        # dealing with Fan Posts
        elif status == 6:
            extract_and_write_fan_posts(elements, name)
            return

        # dealing with Group Members
        elif status == 7:
            # get profile links of members
            extract_and_write_group_members(elements, name)

        """Write results to file"""
        if status == 0:
            for i, _ in enumerate(results):
                # friend's profile link
                f.writelines(results[i])
                f.write(",")

                # friend's name
                f.writelines(people_names[i])
                f.write(",")

                # friend's downloaded picture id
                f.writelines(img_names[i])
                f.write("\n")

        elif status == 1:
            for i, _ in enumerate(results):
                # image's link
                f.writelines(results[i])
                f.write(",")

                # downloaded picture id
                f.writelines(img_names[i])
                f.write("\n")

        elif status == 2:
            for x in results:
                f.writelines(x + "\n")

        elif status == 7:
            for i, _ in enumerate(results):
                # friend's profile link
                f.writelines(results[i])
                f.write(",")

                # friend's name
                f.writelines(people_names[i])
                f.write(",")

        f.close()

    except Exception:
        print("Exception (save_to_file)", "Status =",
              str(status), sys.exc_info())
        pass

    return


# ----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def scrape_data(url, scan_list, section, elements_path, save_status, file_names):
    """Given some parameters, this function can scrap friends/photos/videos/about/posts(statuses) of a profile"""
    page = []

    if save_status == 4 or save_status == 5 or save_status == 6:
        page.append(url)

    page += [url + s for s in section]

    for i, _ in enumerate(scan_list):
        try:
            driver.get(page[i])

            if (
                (save_status == 0) or (save_status == 1) or (save_status == 2)
            ):  # Only run this for friends, photos and videos

                # the bar which contains all the sections
                sections_bar = driver.find_element_by_xpath(
                    selectors.get("sections_bar")
                )

                if sections_bar.text.find(scan_list[i]) == -1:
                    continue
            if save_status == 7:
                if debug_mode == 1:
                    utils.scroll(total_scrolls, driver, selectors, scroll_time)
                else:
                    utils.scroll_to_bottom(driver)
            elif save_status != 3:
                utils.scroll(total_scrolls, driver, selectors, scroll_time)
                pass

            data = driver.find_elements_by_xpath(elements_path[i])

            save_to_file(file_names[i], data, save_status, i)

        except Exception:
            print(
                "Exception (scrape_data)",
                str(i),
                "Status =",
                str(save_status),
                sys.exc_info(),
            )


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def create_original_link(url):
    if url.find(".php") != -1:
        original_link = (
            facebook_https_prefix + facebook_link_body + ((url.split("="))[1])
        )

        if original_link.find("&") != -1:
            original_link = original_link.split("&")[0]

    elif url.find("fnr_t") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + ((url.split("/"))[-1].split("?")[0])
        )
    elif url.find("_tab") != -1:
        original_link = (
            facebook_https_prefix
            + facebook_link_body
            + (url.split("?")[0]).split("/")[-1]
        )
    else:
        original_link = url

    return original_link


def scrap_profile():
    data_folder = os.path.join(os.getcwd(), "data")
    utils.create_folder(data_folder)
    os.chdir(data_folder)

    # execute for all profiles given in input.txt file
    url = driver.current_url
    user_id = create_original_link(url)

    print("\nScraping:", user_id)

    try:
        target_dir = os.path.join(data_folder, user_id.split("/")[-1])
        utils.create_folder(target_dir)
        os.chdir(target_dir)
    except Exception:
        print("Some error occurred in creating the profile directory.")
        os.chdir("../..")
        return

    #to_scrap = ["Friends", "Photos", "Videos", "About", "Posts"]
    to_scrap = ["FanPosts"]
    for item in to_scrap:
        print("----------------------------------------")
        print("Scraping {}..".format(item))

        if item == "Posts" or item == "FanPosts":
            scan_list = [None]
        elif item == "About":
            scan_list = [None] * 7
        else:
            scan_list = params[item]["scan_list"]

        section = params[item]["section"]
        elements_path = params[item]["elements_path"]
        file_names = params[item]["file_names"]
        save_status = params[item]["save_status"]

        scrape_data(user_id, scan_list, section,
                    elements_path, save_status, file_names)

        print("{} Done!".format(item))

    print("Finished Scraping Profile " + str(user_id) + ".")
    os.chdir("../..")

    return


def get_post_message():
    messages = []
    try:
        data = driver.find_elements_by_xpath(selectors.get("post_message"))

        for d in data:
            try:
                # print(d.text)
                if d.text != '':
                    messages.append(d.text+'\n')
            except Exception:
                pass
    except Exception:
        pass
    return messages


def get_comments():
    comments = []
    start = time.time()
    try:
        data = driver.find_element_by_xpath(selectors.get("comment_section"))
        reply_links = driver.find_elements_by_xpath(
            selectors.get("more_comment_replies")
        )
        for link in reply_links:
            try:
                driver.execute_script("arguments[0].click();", link)
            except Exception as e:
                print(e)
                pass
        see_more_links = driver.find_elements_by_xpath(
            selectors.get("comment_see_more_link")
        )
        for link in see_more_links:
            try:
                driver.execute_script("arguments[0].click();", link)
            except Exception as e:
                print(e)
                pass
        replytime = time.time()
        data = driver.find_elements_by_xpath(selectors.get("comment"))
        for d in data:
            try:
                author = d.find_element_by_xpath(
                    selectors.get("comment_author")).text
                profile = d.find_element_by_xpath(selectors.get(
                    "comment_author_href")).get_attribute('href')
                #profile = profile[0:profile.find('?comment_id')]
                regex = re.compile('.+\/groups\/\w+\/user\/(\d+)\/.')
                profile = regex.findall(profile)[0]
                text = d.text
                replies = utils.get_replies(d, selectors)
                comments.append({'author': author, 'text': text,
                                'profile': profile, 'replies': replies})
            except Exception as e:
                print(e)
                pass
        end = time.time()
        print("end - start:" + str(end-start))
        print("end - reply:" + str(end-replytime))
    except Exception as e:
        print(e)
        pass

    return comments


@retry(delay=1, tries=4, backoff=2)
def getfulltime(hov, driver, selector, celement, notification):
    #hovertime(driver, celement)
    fulltime = driver.find_element_by_xpath(selector).text
    if fulltime == '':
        print('raise getfulltime')
        notification = driver.find_element_by_xpath(notification)
        hov.move_to_element(notification).click().perform()
        hovertime(driver, celement)
        raise
    return fulltime


@retry(delay=1, tries=4, backoff=2)
def hovertime(driver, celement):
    try:
        hov = ActionChains(driver)
        hov.move_to_element(celement).perform()
        sleep(0.8)
    except Exception:
        print('raise hovertime')
        raise


def get_group_post_as_line(post_id, photos_dir, latest_time=None):
    try:

        indbComments = []
        indbLikes = []
        post = storage.get_post(post_id)
        if post and 'post_id' in post.keys():
            indbComments = post['comments']
            indbLikes = post['interactions']

        material = {}
        data = driver.find_element_by_xpath(selectors.get("single_post"))
        print('post_id:'+post_id)
        # print(data)
        print('================================')
        ctimes = driver.find_elements_by_xpath(selectors.get("time"))
        cnt = 0
        ctime = ''
        try:
            for celement in ctimes:
                simpletime = celement.text
                print(simpletime)
                regex = re.compile("\d+年\d+月\d+日\w*")
                arr_time = regex.findall(simpletime)
                print(arr_time)
                if len(arr_time) == 0:
                    simpletime = datetime.now().strftime('%m月%d日')
                try:
                    try:
                        hov = ActionChains(driver)
                        hov.move_to_element(celement).perform()
                    except Exception:
                        print('raise hovertime')
                    sleep(0.8)
                    #fulltime = driver.find_element_by_xpath().text
                    fulltime = getfulltime(hov, driver, selectors.get(
                        "ctime"), celement, selectors.get("notification"))
                except Exception:
                    pass

                if(fulltime):
                    ctime = fulltime
                elif len(arr_time) != 0:
                    ctime = arr_time[0]
                print("ctime:" + ctime)
                print("full time:" + fulltime)
                break
                #datetime_object = datetime.strptime(celement.text, '%m/%d/%y %H:%M:%S')
                '''
                hov = ActionChains(driver)
                hov.move_to_element(celement).perform()
                sleep(0.1)
                ctime = driver.find_element_by_xpath(selectors.get("ctime")).text
                #ctext = utils.get_time(data, selectors)
                print(ctime)
                cnt = cnt + 1
                if ctime is not '':
                    break
                '''
        except Exception:
            print('get ctime error')
            ctime = simpletime
            pass

        #ctime = utils.get_time(data, selectors)

        # if latest_time != None and latest_time >= time.strptime(ctime, '%Y年%m月%d日 %A%p%I:%M'):
        #    return ''
        category = ''
        title = ''
        try:

            category = data.find_elements_by_xpath(
                selectors.get("category"))[0].text
        except exceptions.StaleElementReferenceException:
            print('get category StaleElementReferenceException')
            driver.get(utils.create_post_link(post_id, selectors))
            return get_group_post_as_line(post_id, photos_dir)
        except Exception:
            print('get category error')
            pass
        print('get title')
        try:
            title = utils.get_title(data, selectors).text
        except Exception:
            print('get title error')
            pass
        print("category:" + category)
        print("title:" + title)
        # link, status, title, type = get_status_and_title(title,data)
        #link = utils.get_div_links(data, "a", selectors)
        # if link != "":
        #    link = link.get_attribute("href")
        link = ""
        post_type = ""
        users = []
        #status = '"' + utils.get_status(data, selectors).replace("\r\n", " ") + '"'
        try:
            print('get response')
            try:
                status = utils.get_status(driver, data, selectors)
                count = int(status.text.split('\n')[0])
                hov = ActionChains(driver)
                hov.move_to_element(status).click().perform()
                sleep(1)
                #popupdiv = driver.find_element_by_xpath(selectors.get("status_all_list"))
                # get the scroll window
                mooddiv = driver.find_elements_by_xpath(
                    selectors.get("status_mood"))
                mooddiv = mooddiv[len(mooddiv)-1]
                print(count)
                # FB if there is a notification
                # this will get the notification window
                # we need to force to get the last one
                for i in range(int(count/5+1)):
                    print('scroll:' + str(i))
                    try:
                        driver.execute_script(
                            "arguments[0].scrollIntoView(true);", mooddiv)
                        sleep(2)
                    except Exception as e:
                        print(e)

                try:
                    user_list = driver.find_elements_by_xpath(
                        selectors.get("status_user_list"))
                    #user_list = datas.find_elements_by_xpath(selectors.get("status_user_list"))
                except Exception as e:
                    print(e)
                finally:
                    index = 1
                    for user in user_list:
                        if user.text is not '' and '#' not in user.text:
                            print(str(index) + ":" + user.text)
                            index += 1
                            users.append({'url': user.get_attribute('href'),
                                          'name': user.text})
            except Exception as e:
                print(e)
                pass
            finally:

                print('response close start')
                try:
                    divclose = driver.find_element_by_xpath(
                        selectors.get("status_divclose"))
                    close = divclose.find_element_by_xpath(
                        selectors.get("status_close"))
                    hov.move_to_element(close).click().perform()
                    sleep(0.1)
                except Exception as e:
                    print(e)
                    pass
                print('reponse close end')
                # print(status_list.get_attribute('innerHTML'))
        except Exception:
            print('get status error:' + sys.exc_info())
            pass

        print('get photo')
        try:
            photos = utils.get_post_photos_links(
                data, selectors, photos_small_size)
        except Exception:
            print('get photo error:' + sys.exc_info())
            pass
        print('get message')
        post_message = get_post_message()
        print(post_message)
        #post_message = data.text
        print('get comments')
        comments = get_comments()
        download_photos = image_downloader(photos, photos_dir)
        print('download photos done')
        # Update comments and likes
        commentIdx = len(indbComments)
        for i in range(commentIdx, len(comments)-1, 1):
            comments[i]['etlStatus'] = False
            indbComments.append(comments[i])

        likeIdx = len(indbLikes)
        for i in range(likeIdx, len(users)-1, 1):
            users[i]['etlStatus'] = False
            indbLikes.append(users[i])
        locale.setlocale(locale.LC_ALL, 'zh_TW.utf-8')
        material['post_id'] = post_id
        material['time'] = ctime

        print(' get postiostime')
        db_post = storage.get_fbpost(post_id)
        postisotime = ''
        if ctime == '':
            print('get ctime error')
            retry_list.append(post_id)
            sleep(10)
        else:
            postisotime = re.sub('星期.', '', ctime)
        print(postisotime)
        if (db_post is None or 'postiostime' not in db_post) and postisotime != '':
            try:
                locale.setlocale(locale.LC_ALL, 'zh_TW.utf-8')
                postisotime = datetime.strptime(
                    postisotime, "%Y年%m月%d日 %p%I:%M")
            except:
                try:
                    postisotime = datetime.strptime(postisotime, "%Y年%m月%d日")
                except:
                    postisotime = datetime.strptime(postisotime, "%m月%d日")
            postisotime = timezone('Asia/Taipei').localize(postisotime)
        elif db_post is not None and 'postiostime' in db_post:
            postisotime = db_post.postisotime
        else:
            postisotime = ctime
        material['postisotime'] = postisotime
        material['title'] = title
        material['link'] = link
        material['message'] = post_message
        material['comments'] = indbComments
        material['photos'] = photos
        material['download_photos'] = download_photos
        material['category'] = category
        material['interactions'] = indbLikes
        # storage.insert_posts(material)

        print('=======material =========')
        print(material)
        storage.update_post(material)
        line = (
            str(ctime)
            + "||"
            + str(post_type)
            + "||"
            + str(title)
            + "||"
            + str(users)
            + "||"
            + str(link)
            + "||"
            + str(post_id)
            + "||"
            + str(photos)
            + "||"
            + "\n# " + str(post_message)
            + "||"
            + str(comments)
            + "\n"
            + "-----------------------------------------------"
            + "\n"
        )
        return line
    except Exception:
        frame = inspect.currentframe()
        # __FILE__
        fileName = frame.f_code.co_filename
        # __LINE__
        fileNo = frame.f_lineno
        print(fileName + str(fileNo) + 'unexpected error:', sys.exc_info())
        return ''


def create_folders():
    """
    Creates folder for saving data (profile, post or group) according to current driver url
    Changes current dir to target_dir
    :return: target_dir or None in case of failure
    """
    folder = os.path.join(os.getcwd(), "data")
    utils.create_folder(folder)
    os.chdir(folder)
    try:
        item_id = get_item_id(driver.current_url)
        target_dir = os.path.join(folder, item_id)
        utils.create_folder(target_dir)
        os.chdir(target_dir)
        return target_dir
    except Exception:
        print("Some error occurred in creating the group directory.")
        os.chdir("../..")
        return None


def get_item_id(url):
    """
    Gets item id from url
    :param url: facebook url string
    :return: item id or empty string in case of failure
    """
    ret = ""
    try:
        link = create_original_link(url)
        print(link)
        ret = link.split("/")[-1]
        if ret.strip() == "":
            ret = link.split("/")[-2]
    except Exception as e:
        print("Failed to get id: " + format(e))
    return ret


def scrape_group(url):
    if create_folders() is None:
        return
    group_id = get_item_id(url)
    # execute for all profiles given in input.txt file
    print("\nScraping:", group_id)

    to_scrap = ["GroupPosts"]  # , "Photos", "Videos", "About"]
    for item in to_scrap:
        print("----------------------------------------")
        print("Scraping {}..".format(item))

        if item == "GroupPosts":
            scan_list = [None]
        elif item == "About":
            scan_list = [None] * 7
        else:
            scan_list = params[item]["scan_list"]

        section = params[item]["section"]
        elements_path = params[item]["elements_path"]
        file_names = params[item]["file_names"]
        save_status = params[item]["save_status"]

        scrape_data(url, scan_list, section,
                    elements_path, save_status, file_names)

        print("{} Done!".format(item))

    print("Finished Scraping Group " + str(group_id) + ".")
    os.chdir("../..")

    return


def scrape_groupmembers(url):
    if create_folders() is None:
        return
    group_id = get_item_id(url)
    # execute for all profiles given in input.txt file
    print("\nScraping:", group_id)

    to_scrap = ["GroupMembers"]  # , "Photos", "Videos", "About"]
    for item in to_scrap:
        print("----------------------------------------")
        print("Scraping {}..".format(item))

        if item == "GroupPosts":
            scan_list = [None]
        elif item == "About":
            scan_list = [None] * 7
        else:
            scan_list = params[item]["scan_list"]

        section = params[item]["section"]
        elements_path = params[item]["elements_path"]
        file_names = params[item]["file_names"]
        save_status = params[item]["save_status"]

        scrape_data(url, scan_list, section,
                    elements_path, save_status, file_names)

        print("{} Done!".format(item))

    print("Finished Scraping Group " + str(group_id) + ".")
    os.chdir("../..")

    return


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def login(email, password):
    """ Logging into our own profile """

    try:
        global driver
        if _platform == 'linux':
            display = Display(visible=0, size=(800, 800))
            display.start()
        options = Options()

        #  Code to disable notifications pop up of Chrome Browser
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        # options.add_argument("--headless")

        try:
            driver = webdriver.Chrome(
                executable_path=ChromeDriverManager().install(), options=options
            )
        except Exception:
            print("Error loading chrome webdriver " + sys.exc_info())
            exit(1)

        fb_path = facebook_https_prefix + facebook_link_body
        driver.get(fb_path)
        driver.maximize_window()
        driver.implicitly_wait(15)

        # filling the form
        driver.find_element_by_name("email").send_keys(email)
        driver.find_element_by_name("pass").send_keys(password)

        try:
            # clicking on login button
            driver.find_element_by_id("loginbutton").click()
        except NoSuchElementException:
            # Facebook new design
            driver.find_element_by_name("login").click()

        # if your account uses multi factor authentication
        mfa_code_input = utils.safe_find_element_by_id(
            driver, "approvals_code")

        if mfa_code_input is None:
            return

        mfa_code_input.send_keys(input("Enter MFA code: "))
        driver.find_element_by_id("checkpointSubmitButton").click()

        # there are so many screens asking you to verify things. Just skip them all
        while (
            utils.safe_find_element_by_id(
                driver, "checkpointSubmitButton") is not None
        ):
            dont_save_browser_radio = utils.safe_find_element_by_id(
                driver, "u_0_3")
            if dont_save_browser_radio is not None:
                dont_save_browser_radio.click()

            driver.find_element_by_id("checkpointSubmitButton").click()

    except Exception:
        print("There's some error in log in.")
        print(sys.exc_info())
        exit(1)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


def scraper(**kwargs):

    with open("credentials.yaml", "r") as ymlfile:
        cfg = yaml.safe_load(stream=ymlfile)

    if ("password" not in cfg) or ("email" not in cfg):
        print("Your email or password is missing. Kindly write them in credentials.txt")
        exit(1)
    if ("TELEGRAM_TOKEN" not in cfg) or ("CHAT_ID" not in cfg):
        print("Your TELEGRAM_TOKEN or CHAT_ID is missing. Kindly write them in credentials.yaml")
        exit(1)
    global ACCESS_KEY
    global SECRET_KEY
    global BUCKET_ID
    ACCESS_KEY = str(cfg['ACCESS_KEY'])
    SECRET_KEY = str(cfg['SECRET_KEY'])
    BUCKET_ID = str(cfg['BUCKET_ID'])
    apiURL = TELEGRAM_API_ROOT + 'bot' + \
        str(cfg['TELEGRAM_TOKEN']) + '/sendMessage?chat_id=' + \
        str(cfg['CHAT_ID']) + '&text=fb_scraper action: \n'
    req = apiURL + 'start...'
    requests.get(req)

    for line in open("input.txt"):
        print(line + "::")
    urls = [
        line.split(';')[0]
        for line in open("input.txt")
        if not line.lstrip().startswith("#") and not line.strip() == ""
    ]
    dbs = [
        line.split(';')[1].replace('\n', '')
        for line in open("input.txt")
        if not line.lstrip().startswith("#") and not line.strip() == ""
    ]

    if len(urls) > 0:
        print("\nStarting Scraping...")
        login(cfg["email"], cfg["password"])
        for url in urls:
            storage.set_collection(dbs[0])
            driver.get(url)
            link_type = utils.identify_url(driver.current_url)
            if link_type == 0:
                scrap_profile()
            elif link_type == 1:
                # scrap_post(url)
                pass
            elif link_type == 2:
                scrape_group(driver.current_url)
            elif link_type == 3:
                file_name = params["GroupPosts"]["file_names"][0]
                item_id = get_item_id(driver.current_url)
                if create_folders() is None:
                    continue
                f = create_post_file(file_name)
                add_group_post_to_file(f, file_name, item_id)
                f.close()
                os.chdir("../..")
            elif link_type == 4:
                scrape_groupmembers(driver.current_url)
        driver.close()
    else:
        print("Input file is empty.")

    req = apiURL + 'end.'
    requests.get(req)


# -------------------------------------------------------------
# -------------------------------------------------------------
# -------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    # PLS CHECK IF HELP CAN BE BETTER / LESS AMBIGUOUS
    ap.add_argument(
        "-dup",
        "--uploaded_photos",
        help="download users' uploaded photos?",
        default=True,
    )
    ap.add_argument(
        "-dfp", "--friends_photos", help="download users' photos?", default=True
    )
    ap.add_argument(
        "-fss",
        "--friends_small_size",
        help="Download friends pictures in small size?",
        default=True,
    )
    ap.add_argument(
        "-pss",
        "--photos_small_size",
        help="Download photos in small size?",
        default=True,
    )
    ap.add_argument(
        "-ts",
        "--total_scrolls",
        help="How many times should I scroll down?",
        default=2500,
    )
    ap.add_argument(
        "-st", "--scroll_time", help="How much time should I take to scroll?", default=8
    )

    args = vars(ap.parse_args())
    print(args)

    # ---------------------------------------------------------
    # Global Variables
    # ---------------------------------------------------------

    # whether to download photos or not
    download_uploaded_photos = utils.to_bool(args["uploaded_photos"])
    download_friends_photos = utils.to_bool(args["friends_photos"])

    # whether to download the full image or its thumbnail (small size)
    # if small size is True then it will be very quick else if its false then it will open each photo to download it
    # and it will take much more time
    friends_small_size = utils.to_bool(args["friends_small_size"])
    photos_small_size = utils.to_bool(args["photos_small_size"])

    total_scrolls = int(args["total_scrolls"])
    scroll_time = int(args["scroll_time"])

    current_scrolls = 0
    old_height = 0

    driver = None

    with open("selectors.json") as a, open("params.json") as b:
        selectors = json.load(a)
        params = json.load(b)

    firefox_profile_path = selectors.get("firefox_profile_path")
    facebook_https_prefix = selectors.get("facebook_https_prefix")
    facebook_link_body = selectors.get("facebook_link_body")

    # get things rolling
    scraper()
