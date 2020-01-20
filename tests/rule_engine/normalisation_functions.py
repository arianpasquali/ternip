import unittest
from ternip.rule_engine.normalisation_functions.string_conversions import *
from ternip.rule_engine.normalisation_functions.words_to_num import *
from ternip.rule_engine.normalisation_functions.date_functions import *
from ternip.rule_engine.normalisation_functions.relative_date_functions import *

class DateFunctionsTest(unittest.TestCase):
    
    def test_normalise_two_year_date_full(self):
        self.assertEqual('1989', normalise_two_digit_year('1989'))
    
    def test_normalise_two_year_date_full_just_year(self):
        self.assertEqual('1989', normalise_two_digit_year('19890101'))
    
    def test_normalise_two_year_date_apostrophe(self):
        self.assertEqual('1992', normalise_two_digit_year("'92"))
    
    def test_normalise_two_year_date_apostrophe_future(self):
        self.assertEqual('2018', normalise_two_digit_year("'18"))
    
    def test_normalise_two_year_date_two_year(self):
        self.assertEqual('1992', normalise_two_digit_year("92"))
    
    def test_normalise_two_year_date_two_year_future(self):
        self.assertEqual('2018', normalise_two_digit_year("18"))
    
    def test_normalise_two_year_date_first_millenium(self):
        self.assertEqual('0906', normalise_two_digit_year('906'))
    
    def test_easter_date_string(self):
        self.assertEqual('20100404', easter_date('2010'))
    
    def test_easter_date_int(self):
        self.assertEqual('20100404', easter_date(2010))
    
    def test_date_to_week(self):
        self.assertEqual('2010W31', date_to_week(2010, 8, 3))
    
    def test_date_to_dow_normal(self):
        self.assertEqual(2, date_to_dow(2010, 8, 3))
    
    def test_date_to_dow_wraparound(self):
        self.assertEqual(0, date_to_dow(2010, 8, 1))
    
    def test_nth_dow_to_day_normal(self):
        self.assertEqual(3, nth_dow_to_day((8, 2, 1), 2010))
    
    def test_nth_dow_to_day_special_case(self):
        self.assertEqual(8, nth_dow_to_day((8, 7, 2), 2010))
    
    def test_nth_dow_to_day_special_case2(self):
        self.assertEqual(12, nth_dow_to_day((7, 1, 2), 2010))
    
    def test_date_to_iso_alreadyiso(self):
        self.assertEqual('20100808', date_to_iso('20100808'))
        self.assertEqual('20100808', date_to_iso('2010-08-08'))
        self.assertEqual('20100808T144026', date_to_iso('20100808T144026'))
        self.assertEqual('20100808T144026', date_to_iso('2010-08-08T14:40:26'))
        self.assertEqual('20100808T144026+0100', date_to_iso('20100808 T 144026 + 0100'))
        self.assertEqual('20100808T144026+0100', date_to_iso('2010-08-08T14:40:26+0100'))
        self.assertEqual('T144026+0100', date_to_iso('T14:40:26+0100'))
        self.assertEqual('T144026', date_to_iso('T14:40:26'))
        self.assertEqual('T144026', date_to_iso('T144026'))
    
    def test_date_to_iso_ace(self):
        self.assertEqual('20100808T1625', date_to_iso('20100808:1625'))
    
    def test_date_to_iso_date(self):
        self.assertEqual('20101006', date_to_iso('6 October 2010'))
        self.assertEqual('20101006', date_to_iso('6th October 2010'))
        self.assertEqual('20101006', date_to_iso('October 6th 2010'))
        self.assertEqual('20101010', date_to_iso('October Tenth 2010'))
        self.assertEqual('20100810', date_to_iso('2010/08/10'))
        self.assertEqual('20101031', date_to_iso('31/10/2010'))
        self.assertEqual('20101031', date_to_iso('10/31/2010'))
        self.assertEqual('20101008', date_to_iso('October 8 2010'))
        self.assertEqual('19991008', date_to_iso('October 8 99'))
    
    def test_date_to_iso_time(self):
        self.assertEqual('20101008T1628', date_to_iso('October 8th 2010 16:28'))
        self.assertEqual('XXXXXXXXT1628', date_to_iso('16:28'))
        self.assertEqual('XXXXXXXXT1628', date_to_iso('4:28 PM'))
        self.assertEqual('XXXXXXXXT1628+0200', date_to_iso('16:28 GMT+0200'))
        self.assertEqual('XXXXXXXXT1628Z', date_to_iso('16:28 GMT'))
        self.assertEqual('XXXXXXXXT1628-0500', date_to_iso('16:28 EST'))
        self.assertEqual('XXXXXXXXT1628-0400', date_to_iso('16:28 EDT'))
        self.assertEqual('XXXXXXXXT1628+0200', date_to_iso('16:28 RDT'))
        self.assertEqual('XXXXXXXXT1628', date_to_iso('1628 4/2'))
        self.assertEqual('XXXXXXXXT1628', date_to_iso('1628 hours 4/2'))
        self.assertEqual('XXXXXXXXT162808.02', date_to_iso('16:28:08.02'))
        self.assertEqual('XXXXXXXXT162808', date_to_iso('16:28:08'))
    
    def test_extract_timezone(self):
        self.assertEqual('RDT', extract_timezone('18:26 RDT'))
        self.assertEqual('PST', extract_timezone('<PST~.+>'))
        self.assertEqual('UT', extract_timezone('<Universal~.+>'))
        self.assertEqual('GMT', extract_timezone('<zulu~.+>'))
        self.assertEqual('EST', extract_timezone('<Eastern~.+><standard~.+><time~.+>'))
    
    def test_convert_to_24_hours(self):
        self.assertEqual(18, convert_to_24_hours(6, 'p'))
        self.assertEqual(6, convert_to_24_hours(6, 'a'))
        self.assertEqual(20, convert_to_24_hours(20, 'a'))

class StringConversionsTest(unittest.TestCase):
    
    def test_month_to_num_abbr(self):
        self.assertEqual(4, month_to_num('apr'))
    
    def test_month_to_num_full(self):
        self.assertEqual(4, month_to_num('April'))
    
    def test_month_to_num_mixed(self):
        self.assertEqual(6, month_to_num('JUNE'))
    
    def test_month_to_num_invalid(self):
        self.assertEqual(0, month_to_num('Frentober'))
    
    def test_day_to_num_full(self):
        self.assertEqual(0, day_to_num('sunday'))
    
    def test_month_to_num_mixed(self):
        self.assertEqual(5, day_to_num('FRIDAY'))
    
    def test_month_to_num_mixed(self):
        self.assertEqual(7, day_to_num('frankfurter'))
    
    def test_decade_num(self):
        self.assertEqual(9, decade_nums('nine'))
    
    def test_decade_num_mixed(self):
        self.assertEqual(8, decade_nums('EiGH'))
    
    def test_decade_num_bad(self):
        self.assertEqual(1, decade_nums('twenty-seven'))
    
    def test_season(self):
        self.assertEqual('SP', season('spring'))
    
    def test_season_mixed(self):
        self.assertEqual('WI', season('WINTER'))
    
    def test_season_bad(self):
        self.assertEqual('hunting', season('hunting'))
    
    def test_units_to_gran(self):
        self.assertEqual('D', units_to_gran('day'))
    
    def test_units_to_gran_mixed(self):
        self.assertEqual('C', units_to_gran('CENTURY'))
    
    def test_units_to_gran_bad(self):
        self.assertEqual('bad', units_to_gran('bad'))
    
    def test_fixed_holiday_date(self):
        self.assertEqual('1225', fixed_holiday_date('christmas'))
    
    def test_fixed_holiday_date_mixed(self):
        self.assertEqual('0423', fixed_holiday_date('<Saint~NNP><George~NNP>'))
    
    def test_fixed_holiday_date_bad(self):
        self.assertEqual('', fixed_holiday_date('bad'))
    
    def test_nth_dow_holiday_date(self):
        self.assertEqual((1, 1, 3), nth_dow_holiday_date('king'))
    
    def test_nth_dow_holiday_date_mixed(self):
        self.assertEqual((11, 4, 4), nth_dow_holiday_date('ThanksGiving'))
    
    def test_nth_dow_holiday_date_bad(self):
        self.assertEqual((0,0,0), nth_dow_holiday_date('bad'))
    
    def test_season_to_month_id(self):
        self.assertEqual('december', season_to_month('WI'))
    
    def test_season_to_month_name(self):
        self.assertEqual('september', season_to_month('autumn'))
    
    def test_season_to_month_bad(self):
        self.assertEqual('', season_to_month('foobar'))
    
    def test_build_duration_value(self):
        self.assertEqual('XM', build_duration_value('X', 'month'))
        self.assertEqual('6X', build_duration_value(6, 'pineapples'))
        self.assertEqual('T10M', build_duration_value(10, 'minute'))
        self.assertEqual('12D', build_duration_value(12, 'day'))
        self.assertEqual('700Y', build_duration_value(7, 'century'))

class WordsToNumTest(unittest.TestCase):
    
    def test_ordinal_number(self):
        self.assertEqual(6, ordinal_to_num('6th'))
    
    def test_ordinal_word(self):
        self.assertEqual(18, ordinal_to_num('eighteenth'))
    
    def test_ordinal_bad(self):
        self.assertEqual(1, ordinal_to_num('beefburger'))
    
    def test_words_to_num_simple(self):
        self.assertEqual(8, words_to_num("eight"))
    
    def test_words_to_num_none(self):
        self.assertEqual(0, words_to_num(None))
    
    def test_words_to_num_a(self):
        self.assertEqual(100, words_to_num('a hundred'))
    
    def test_words_to_num_the(self):
        self.assertEqual(6, words_to_num('the six'))
    
    def test_words_to_num_and(self):
        self.assertEqual(326, words_to_num('three hundred and twenty six'))
    
    def test_words_to_num_and(self):
        self.assertEqual(7320, words_to_num('seven thousand, three hundred and twenty'))
    
    def test_words_to_num_mixed(self):
        self.assertEqual(1806, words_to_num('18 hundred and six'))
    
    def test_words_to_num_mixed(self):
        self.assertEqual(324, words_to_num('<324~.+>'))
    
    def test_words_to_num_marked_up(self):
        self.assertEqual(4, words_to_num('NUM_START<four~CD>NUM_END'))
    
    def test_words_to_num_mixed(self):
        self.assertEqual(0, words_to_num('six hundred and bread'))
    
    def test_words_to_num_ordinal(self):
        self.assertEqual(92, words_to_num('ninety second'))
    
    def test_words_to_num_bad_ordinal(self):
        self.assertEqual(0, words_to_num('first two'))

class RelativeDateFunctionsTest(unittest.TestCase):
    
    def test_compute_offset_base_yesterday(self):
        self.assertEqual('20100803', compute_offset_base('20100804', 'Yesterday', 1))
        self.assertEqual('20100803', compute_offset_base('20100804', 'yesterday', -1))
    
    def test_compute_offset_base_tomorrow(self):
        self.assertEqual('20100805', compute_offset_base('20100804', 'tomORROW', -1))
        self.assertEqual('20100805', compute_offset_base('20100804', 'tomorrow', 1))
    
    def test_compute_offset_base_no_match(self):
        self.assertEqual('20100804', compute_offset_base('20100804', None, -1))
    
    def test_compute_offset_base_bad_day(self):
        self.assertEqual('20100804', compute_offset_base('20100804', 'nosuchday', -1))
    
    def test_compute_offset_base_last_day(self):
        self.assertEqual('20100730', compute_offset_base('20100804', 'Friday', -1))
        self.assertEqual('20100729', compute_offset_base('20100804', 'thursday', -1))
    
    def test_compute_offset_base_next_day(self):
        self.assertEqual('20100806', compute_offset_base('20100804', 'Friday', 1))
        self.assertEqual('20100810', compute_offset_base('20100804', 'tuesday', 1))
    
    def test_compute_offset_base_closest_day(self):
        self.assertEqual('20100806', compute_offset_base('20100804', 'Friday', 0))
        self.assertEqual('20100803', compute_offset_base('20100804', 'tuesday', 0))
    
    def test_compute_offset_base_today(self):
        self.assertEqual('20100811', compute_offset_base('20100804', 'Wednesday', 1))
        self.assertEqual('20100804', compute_offset_base('20100804', 'Wednesday', 0))
        self.assertEqual('20100728', compute_offset_base('20100804', 'Wednesday', -1))
    
    def test_compute_offset_base_last_month(self):
        self.assertEqual('201006', compute_offset_base('20100804', 'June', -1))
        self.assertEqual('200912', compute_offset_base('20100804', 'dec', -1))
    
    def test_compute_offset_base_next_month(self):
        self.assertEqual('201012', compute_offset_base('20100804', 'DECEMBER', 1))
        self.assertEqual('201101', compute_offset_base('20100804', 'jan', 1))
    
    def test_compute_offset_base_this_month(self):
        self.assertEqual('201108', compute_offset_base('20100804', 'August', 1))
        self.assertEqual('201008', compute_offset_base('20100804', 'August', 0))
        self.assertEqual('200908', compute_offset_base('20100804', 'aug', -1))
    
    def test_compute_offset_base_closest_month(self):
        self.assertEqual('201007', compute_offset_base('20100804', 'July', 0))
        self.assertEqual('201011', compute_offset_base('20100804', 'November', 0))
    
    def test_compute_offset_base_last_fixedhol(self):
        self.assertEqual('20091225', compute_offset_base('20091230', '<christmas~foo>', -1))
        self.assertEqual('20091225', compute_offset_base('20100804', '<christmas~foo>', -1))
    
    def test_compute_offset_base_next_fixedhol(self):
        self.assertEqual('20111225', compute_offset_base('20101231', '<christmas~foo>', 1))
        self.assertEqual('20111225', compute_offset_base('20110426', '<christmas~foo>', 1))
    
    def test_compute_offset_base_this_fixedhol(self):
        self.assertEqual('20101225', compute_offset_base('20101225', '<christmas~foo>', 1))
        self.assertEqual('20101225', compute_offset_base('20101225', '<christmas~foo>', -1))
    
    def test_compute_offset_base_last_nthdowhol(self):
        self.assertEqual('20100620', compute_offset_base('20100806', 'father', -1))
        self.assertEqual('20090621', compute_offset_base('20100618', 'father', -1))
    
    def test_compute_offset_base_next_nthdowhol(self):
        self.assertEqual('20110619', compute_offset_base('20100806', 'father', 1))
        self.assertEqual('20100620', compute_offset_base('20100608', 'father', 1))
    
    def test_compute_offset_base_this_nthdowhol(self):
        self.assertEqual('20100620', compute_offset_base('20100620', 'father', 1))
        self.assertEqual('20100620', compute_offset_base('20100620', 'father', -1))
    
    def test_compute_offset_base_last_lunarhol(self):
        self.assertEqual('20090412', compute_offset_base('20091006', '<easter~foo>', -1))
        self.assertEqual('20090412', compute_offset_base('20100201', '<easter~foo>', -1))
    
    def test_compute_offset_base_next_lunarhol(self):
        self.assertEqual('20100404', compute_offset_base('20100201', '<easter~foo>', 1))
        self.assertEqual('20110424', compute_offset_base('20101006', '<easter~foo>', 1))
    
    def test_compute_offset_base_this_lunarhol(self):
        self.assertEqual('20100404', compute_offset_base('20100404', '<easter~foo>', 1))
        self.assertEqual('20100404', compute_offset_base('20100404', '<easter~foo>', -1))
    
    def test_offset_minute(self):
        self.assertEqual('20100804T1628', offset_from_date('20100804T163604', -8, 'TM'))
        self.assertEqual('20100804T1642', offset_from_date('20100804T1636', 6, 'TM'))
        self.assertEqual('20100804T1504', offset_from_date('20100804T1459', 5, 'TM'))
        self.assertEqual('20100804T1559', offset_from_date('20100804T1709', -70, 'TM'))
    
    def test_offset_hour(self):
        self.assertEqual('20100804T10', offset_from_date('20100804T1836', -8, 'TH'))
        self.assertEqual('20100804T1036', offset_from_date('20100804T1836', -8, 'TH', True))
        self.assertEqual('20100804T22', offset_from_date('20100804T1636', 6, 'TH'))
        self.assertEqual('20100805T06', offset_from_date('20100804T1859', 12, 'TH'))
        self.assertEqual('20100802T22', offset_from_date('20100804T0409', -30, 'TH'))
    
    def test_offset_day(self):
        self.assertEqual('20100401', offset_from_date('20100403T1443', -2))
        self.assertEqual('20100401T1443', offset_from_date('20100403T1443', -2, exact=True))
        self.assertEqual('20100401T14', offset_from_date('20100403T14', -2, exact=True))
        self.assertEqual('20100406', offset_from_date('20100403T1443', 3))
        self.assertEqual('20100403', offset_from_date('20100321T1443', 13))
        self.assertEqual('20080229', offset_from_date('20090301', -366, exact=True))
    
    def test_offset_week(self):
        self.assertEqual('2010W31', offset_from_date('20100820', -2, 'W'))
        self.assertEqual('20100806', offset_from_date('20100820', -2, 'W', True))
        self.assertEqual('2010W01', offset_from_date('20091225', 2, 'W'))
    
    def test_offset_fortnight(self):
        self.assertEqual('2010W29', offset_from_date('20100820', -2, 'F'))
        self.assertEqual('20100731', offset_from_date('20100828', -2, 'F', True))
        self.assertEqual('2010W03', offset_from_date('20091225', 2, 'F'))
    
    def test_offset_month(self):
        self.assertEqual('201006', offset_from_date('20100820', -2, 'M'))
        self.assertEqual('20100628', offset_from_date('20100828', -2, 'M', True))
        self.assertEqual('201004', offset_from_date('200810', 18, 'M'))
        self.assertEqual('20100228', offset_from_date('20100331', -1, 'M', True))
        self.assertEqual('200912', offset_from_date('20100110', -1, 'M'))
        self.assertEqual('20080229', offset_from_date('20100331', -25, 'M', True))
    
    def test_offset_year(self):
        self.assertEqual('1999', offset_from_date('20080812', -9, 'Y'))
        self.assertEqual('20090812', offset_from_date('20080812T1236', 1, 'Y', True))
        self.assertEqual('202008', offset_from_date('200808',12, 'Y', True))
        self.assertEqual('20080229', offset_from_date('20120229', -4, 'Y', True))
        self.assertEqual('20100228', offset_from_date('20120229', -2, 'Y', True))
    
    def test_offset_decade(self):
        self.assertEqual('199', offset_from_date('200908', -1, 'E'))
        self.assertEqual('19990812', offset_from_date('19890812T1236', 1, 'E', True))
    
    def test_offset_century(self):
        self.assertEqual('19', offset_from_date('200908', -1, 'C'))
        self.assertEqual('20990812', offset_from_date('19990812T1236', 1, 'C', True))
    
    def test_offset_generic(self):
        self.assertEqual('PAST_REF', offset_from_date('20100804T1432', -1, 'X'))
        self.assertEqual('FUTURE_REF', offset_from_date('20100804T1432', 1, 'X'))
        self.assertEqual('20100804T1432', offset_from_date('20100804T1432', 0, 'X'))
    
    def test_offset_no_ref_date(self):
        self.assertEqual('PAST_REF', offset_from_date('', -1, 'Y'))
        self.assertEqual('FUTURE_REF', offset_from_date('', 1, 'Y'))
