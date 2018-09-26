import unittest
from werkzeug.exceptions import BadRequestKeyError
import make_a_data_object


class TestFormSubmit(unittest.TestCase):
    """Confused testing: am I testing the app, the class, or controller?"""
    def setUp(self):
        make_a_data_object.app.testing = True
        make_a_data_object.app.logger.setLevel(20)
        self.app = make_a_data_object.app.test_client()
        self.form_input = {
            'abstract': "lorem ipsum something something",
            'precipitation': "1, 2, 3, 4",
            'daylength': "12",
            'smoothing': "",
            'limit': ""}

    def test_minimal_input_satisfied(self):
        rv = self.app.post('/make', data=self.form_input)
        self.assertEqual(200, rv.status_code)

    def test_no_form_input_at_all_is_given(self):
        with self.assertRaises(BadRequestKeyError):
            self.app.post('/make')

    def test_empty_form_is_submitted(self):
        with self.assertRaises(BadRequestKeyError):
            self.app.post('/make', data={})

    def test_smoothing_is_missing(self):
        """Even an empty string is expected."""
        del(self.form_input['smoothing'])
        with self.assertRaisesRegex(TypeError, "not 'NoneType'"):
            self.app.post('/make', data=self.form_input)

    def test_limit_is_missing(self):
        """Even an empty string is expected."""
        del(self.form_input['limit'])
        with self.assertRaisesRegex(TypeError, "not 'NoneType'"):
            self.app.post('/make', data=self.form_input)

    def test_some_unrecognized_form_input_is_given(self):
        """Unknown keys should be just ignored."""
        self.form_input['kittens'] = 'ok they are fluffy'
        rv = self.app.post('/make', data=self.form_input)
        self.assertEqual(200, rv.status_code)

    def test_missing_abstract(self):
        del(self.form_input['abstract'])
        with self.assertRaisesRegex(BadRequestKeyError, "abstract"):
            self.app.post('/make', data=self.form_input)

    def test_empty_abstract(self):
        self.form_input['abstract'] = ""
        with self.assertRaisesRegex(ValueError, "array of size 0"):
            self.app.post('/make', data=self.form_input)

    def test_too_short_abstract(self):
        self.form_input['abstract'] = "kittens"
        with self.assertRaisesRegex(ValueError, 'at least 2 entries'):
            self.app.post('/make', data=self.form_input)

    def test_missing_precipitation(self):
        del(self.form_input['precipitation'])
        with self.assertRaisesRegex(BadRequestKeyError, "precipitation"):
            self.app.post('/make', data=self.form_input)

    def test_empty_precipitation(self):
        self.form_input['precipitation'] = ""
        with self.assertRaisesRegex(ValueError, "could not convert.*to float"):
            self.app.post('/make', data=self.form_input)

    def test_too_short_precipitation(self):
        self.form_input['precipitation'] = "2"
        with self.assertRaisesRegex(ValueError, 'at least 2 entries'):
            self.app.post('/make', data=self.form_input)

    def test_missing_daylength(self):
        del(self.form_input['daylength'])
        with self.assertRaisesRegex(BadRequestKeyError, "daylength"):
            self.app.post('/make', data=self.form_input)

    def test_precipitation_contains_non_numerals(self):
        self.form_input['precipitation'] = "1, 2, kitten, 4"
        with self.assertRaisesRegex(ValueError, 'could not convert.*to float'):
            self.app.post('/make', data=self.form_input)

    def test_daylength_is_not_a_numeral_and_cannot_be_converted(self):
        self.form_input['daylength'] = "kittens are nice"
        with self.assertRaisesRegex(ValueError, "could not convert.*to float"):
            self.app.post('/make', data=self.form_input)


if __name__ == '__main__':
    unittest.main()
