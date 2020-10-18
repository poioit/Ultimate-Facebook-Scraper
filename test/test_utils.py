from unittest import TestCase
from scraper import utils
from scraper import scraper


class Test(TestCase):
    def test_identify_url(self):
        self.assertEqual(
            utils.identify_url("https://www.facebook.com/groups/123456789694/?fref=nf"),
            2,
        )
        self.assertEqual(
            utils.identify_url("https://www.facebook.com/groups/123456789694"), 2
        )
        self.assertEqual(
            utils.identify_url(
                "https://www.facebook.com/groups/12345645546/permalink/213453415513/"
            ),
            3,
        )
        self.assertEqual(
            utils.identify_url("https://www.facebook.com/dfsdfsdf.sdfsdfs"), 0,
        )
        self.assertEqual(
            utils.identify_url("https://www.facebook.com/sdfsdfsd/posts/123456784684"),
            1,
        )
    def test_get_group_post_as_line(self, post_id, photos_dir, latest_time):
        pass
