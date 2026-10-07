import datetime as dt
import unittest
from collect import due

class FrequencyTests(unittest.TestCase):
    def test_daily_checks_use_beijing_calendar_days_instead_of_drifting_by_runtime(self):
        now=dt.datetime(2026,10,7,0,0,tzinfo=dt.timezone.utc)
        s={"enabled":1,"interval_hours":24,"last_checked":"2026-10-06T02:22:00Z","status":"success"}
        self.assertTrue(due(s,now))
        s["last_checked"]="2026-10-07T00:01:00Z"
        self.assertFalse(due(s,now))
    def test_paused_and_weekly_sources_are_not_collected_every_day(self):
        now=dt.datetime(2026,10,7,0,0,tzinfo=dt.timezone.utc)
        self.assertFalse(due({"enabled":0},now))
        self.assertFalse(due({"enabled":1,"interval_hours":168,"last_checked":"2026-10-06T00:00:00Z"},now))
        self.assertTrue(due({"enabled":1,"interval_hours":168,"last_checked":"2026-09-30T00:00:00Z"},now))
    def test_running_leases_prevent_overlapping_collectors(self):
        now=dt.datetime(2026,10,7,0,1,tzinfo=dt.timezone.utc)
        self.assertFalse(due({"enabled":1,"interval_hours":24,"last_checked":"2026-10-06T23:59:00Z","status":"running"},now))

if __name__=="__main__":
    unittest.main()
