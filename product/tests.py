from django.test.testcases import TestCase

from .services.selector import ExtractChoreography


class ProcessTest(TestCase):
    def setUp(self):
        self.__eob = ExtractChoreography([""])
        self.__eob.get_music_similarity_score([3, 5, 1])
        self.__eob.set_song_score([[3, 5, 6, 8], [4, 10, 1, 5, 10], [3, 1, 5]])
        self.__eob.set_choreo_score([[5, 9, 1, 10], [10, 2, 5, 8, 2], [4, 10, 3]])

    def test_extract_harmony_score(self):
        expected_res = [3.25, 5.8, 4.0]
        test_harmony_res = self.__eob.extract_harmony_score()
        self.assertEquals(expected_res, test_harmony_res)

    def test_normalize_scores(self):
        self.__eob._harmony_unnormalized = [3.25, 5.8, 4.0]  # harmony unnormalized 는 위의 과정을 거쳐야 됨
        expected_res = ([75.0, 100.0, 50.0],
                        [50.0, 100.0, 64.70588235294117])
        test_res = self.__eob.normalize_scores()
        self.assertEquals(expected_res, test_res)

    def test_avg_scores(self):
        expected_res = [62.5, 100.0, 57.35294117647059]
        self.__eob._harmony_unnormalized = [3.25, 5.8, 4.0]
        self.__eob._similarity_normalized, self.__eob._harmony_normalized = ([75.0, 100.0, 50.0],
                                                                             [50.0, 100.0, 64.70588235294117])
        test_res = self.__eob.avg_scores()
        self.assertEquals(expected_res, test_res)

    def test_final_scores(self):
        expected_res = [62.5, 100.0, 57.35294117647059]
        test_res = self.__eob.extract_final_score()
        self.assertEquals(expected_res, test_res)
