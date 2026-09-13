import re
import uuid
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from icalendar import Alarm, Calendar, Event

WEEK1_MON = date(2026, 9, 7)
TZ = ZoneInfo("Asia/Shanghai")
WEEKDAY_MAP = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

# course_id, course_name, teacher, location, type, start_date, weekday, start_time, end_time, week_range
_RAW_COURSES = [
("C001","现代金融风险管理概论","陈忠阳","修远楼303","repeat","2026-09-10","TH","14:00","17:00","1-2周"),
("C002","现代金融风险管理概论","陈忠阳","修远楼303","repeat","2026-09-10","TH","18:00","21:00","1-2周"),
("C003","现代金融风险管理概论","陈忠阳","修远楼303","repeat","2026-09-11","FR","08:30","11:45","1-2周"),
("C004","现代金融风险管理概论","陈忠阳","修远楼303","repeat","2026-09-11","FR","14:00","17:00","1-2周"),
("C005","现代金融风险管理概论","陈忠阳","修远楼303","repeat","2026-09-11","FR","18:00","21:00","1-2周"),
("C006","现代金融风险管理概论","陈忠阳","修远楼303","repeat","2026-09-12","SA","14:00","17:00","1-2周"),
("C007","市场风险管理与实践","田鑫","修远楼303","repeat","2026-10-18","SU","08:30","11:45","6-8,11周"),
("C008","市场风险管理与实践","田鑫","修远楼303","repeat","2026-10-18","SU","14:00","17:00","6-8,11周"),
("C009","中国式现代化的理论与实践","孙榆慧","图书馆报告厅","repeat","2026-09-13","SU","08:30","11:45","1,10,13-15单周"),
("C010","中国式现代化的理论与实践","孙榆慧","图书馆报告厅","repeat","2026-09-13","SU","14:00","17:00","1,10,13-15单周"),
("C011","金融理论与政策","刘震,瞿强","修远楼303","repeat","2026-11-03","TU","18:00","21:00","9周"),
("C012","金融理论与政策","刘震,瞿强","修远楼303","repeat","2026-11-04","WE","08:30","11:45","9周"),
("C013","金融理论与政策","刘震,瞿强","修远楼303","repeat","2026-11-05","TH","14:00","17:00","9-13周"),
("C014","金融理论与政策","刘震,瞿强","修远楼303","repeat","2026-11-06","FR","08:30","11:45","9-13周"),
("C015","财务报表分析","王英中","修远楼303","repeat","2026-09-18","FR","14:00","17:00","2-13周"),
("C016","投资学","张逸凡,许荣","修远楼303","repeat","2026-11-03","TU","08:30","11:45","9-14周"),
("C017","投资学","张逸凡,许荣","修远楼303","single","2026-12-14","MO","08:30","11:45","15周周一"),
("C018","投资学","张逸凡,许荣","修远楼303","single","2026-12-15","TU","08:30","11:45","15周周二"),
("C019","投资学","张逸凡,许荣","修远楼303","single","2026-12-16","WE","08:30","11:45","15周周三"),
("C020","投资学","张逸凡,许荣","修远楼303","single","2026-12-17","TH","14:00","17:00","15周周四"),
("C021","投资学","张逸凡,许荣","修远楼303","single","2026-12-21","MO","08:30","11:45","16周周一"),
("C022","投资学","张逸凡,许荣","修远楼303","single","2026-12-22","TU","08:30","11:45","16周周二"),
("C023","公司金融","胡学峰,苗萌,李锦璇","修远楼303","repeat","2026-09-15","TU","14:00","17:00","2-7周"),
("C024","公司金融","胡学峰,苗萌,李锦璇","修远楼303","repeat","2026-10-27","TU","14:00","17:00","8周"),
("C025","公司金融","胡学峰,苗萌,李锦璇","修远楼303","repeat","2026-11-03","TU","14:00","17:00","9-11周"),
("C026","公司金融","胡学峰,苗萌,李锦璇","修远楼303","repeat","2026-11-23","MO","18:00","21:00","12周"),
("C027","公司金融","胡学峰,苗萌,李锦璇","修远楼303","repeat","2026-11-24","TU","14:00","17:00","12周"),
("C028","金融计量学","胡学峰","修远楼303","repeat","2026-09-09","WE","08:30","11:45","1-8周"),
("C029","宏观与行业风险分析","胡德宝","修远楼303","repeat","2026-10-14","WE","18:00","21:00","6-9周"),
("C030","智慧治理基础理论","殷赏,黄甄铭,金惠杰","修远楼318","repeat","2026-09-07","MO","18:00","21:00","1-8周"),
("C031","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-09-08","TU","08:30","11:45","1周周二"),
("C032","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-09-09","WE","18:00","21:00","1周周三"),
("C033","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-09-10","TH","08:30","11:45","1周周四"),
("C034","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-09-11","FR","08:30","11:45","1周周五"),
("C035","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-09-16","WE","18:00","21:00","2周周三"),
("C036","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-09-23","WE","18:00","21:00","3周周三"),
("C037","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-09-30","WE","18:00","21:00","4周周三"),
("C038","区块链与金融治理","周逸美,邱志刚","修远楼303","single","2026-10-07","WE","18:00","21:00","5周周三"),
("C039","大数据与金融治理","吴轲,贾诗威","修远楼303","single","2026-11-08","SU","14:00","17:00","9周周日"),
("C040","大数据与金融治理","吴轲,贾诗威","修远楼303","single","2026-11-08","SU","18:00","21:00","9周周日"),
("C041","大数据与金融治理","吴轲,贾诗威","修远楼303","single","2026-11-10","TU","18:00","21:00","10周周二"),
("C042","大数据与金融治理","吴轲,贾诗威","修远楼303","repeat","2026-11-11","WE","08:30","11:45","10-14周"),
("C043","机器学习与量化投资","张逸凡","修远楼303","repeat","2026-11-05","TH","08:30","11:45","9-16周"),
]
_KEYS = ("course_id","course_name","teacher","location","type","start_date","weekday","start_time","end_time","week_range")
COURSES = [dict(zip(_KEYS, row)) for row in _RAW_COURSES]


def parse_week_range(value: str) -> list[int]:
    """解析周次；“单周/双周”仅过滤范围项，显式列出的单周次始终保留。"""
    weeks = []
    parity = "odd" if "单周" in value else "even" if "双周" in value else None
    normalized = value.replace("单周", "").replace("双周", "").replace("周", "")
    for part in normalized.split(","):
        match = re.search(r"(\d+)\s*-\s*(\d+)", part)
        if match:
            start, end = map(int, match.groups())
            if start > end:
                raise ValueError(f"周次范围有误：{part}")
            range_weeks = list(range(start, end + 1))
            if parity == "odd":
                range_weeks = [week for week in range_weeks if week % 2 == 1]
            elif parity == "even":
                range_weeks = [week for week in range_weeks if week % 2 == 0]
            weeks.extend(range_weeks)
        else:
            number = re.search(r"\d+", part)
            if number:
                weeks.append(int(number.group()))
    if not weeks:
        raise ValueError(f"无法解析周次：{value}")
    return sorted(set(weeks))


def get_course_dates(target_weeks: list[int], weekday_idx: int) -> list[date]:
    return [WEEK1_MON + timedelta(days=(week - 1) * 7 + weekday_idx) for week in target_weeks]


def build_ics(selected_course_ids: list[str], holidays: set[date] | None = None) -> bytes:
    holidays = holidays or set()
    calendar = Calendar()
    calendar.add("prodid", "-//RUC SUZHOU Course ICS Generator//ZH")
    calendar.add("version", "2.0")
    calendar.add("calscale", "GREGORIAN")
    now = datetime.now(TZ)

    for row in COURSES:
        if row["course_id"] not in selected_course_ids:
            continue
        weeks = parse_week_range(row["week_range"])
        dates = get_course_dates(weeks, WEEKDAY_MAP[row["weekday"]])
        for class_date in dates:
            if class_date in holidays:
                continue
            start_clock = time.fromisoformat(row["start_time"])
            end_clock = time.fromisoformat(row["end_time"])
            starts_at = datetime.combine(class_date, start_clock, TZ)
            ends_at = datetime.combine(class_date, end_clock, TZ)
            event = Event()
            event.add("uid", f'{row["course_id"]}-{class_date.isoformat()}-{uuid.uuid4().hex[:8]}@ruc-course-cal')
            event.add("dtstamp", now)
            event.add("dtstart", starts_at)
            event.add("dtend", ends_at)
            event.add("summary", row["course_name"])
            event.add("location", row["location"])
            event.add("description", f'教师：{row["teacher"]}\n地点：{row["location"]}')
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("trigger", timedelta(minutes=-15))
            alarm.add("description", f'课程提醒：{row["course_name"]}')
            event.add_component(alarm)
            calendar.add_component(event)
    return calendar.to_ical()


st.set_page_config(page_title="人大苏州金融专硕｜课表 ICS 生成器", page_icon="📅", layout="wide")
st.title("📅 人大苏州校区 金融专硕课表 ICS 生成器")
st.caption("按课程名称选择，一键导出可导入苹果日历、Outlook 和 Google Calendar 的 ICS 文件。")

course_name_to_ids = {}
for item in COURSES:
    course_name_to_ids.setdefault(item["course_name"], []).append(item["course_id"])
course_names = sorted(course_name_to_ids)

if "course_selector" not in st.session_state:
    st.session_state.course_selector = course_names.copy()

left, right = st.columns(2)
if left.button("✅ 全选所有课程", width="stretch"):
    st.session_state.course_selector = course_names.copy()
    st.rerun()
if right.button("❌ 取消全选", width="stretch"):
    st.session_state.course_selector = []
    st.rerun()

selected_names = st.multiselect(
    "选择课程（选择课程名称后会包含其全部上课时段）",
    options=course_names,
    key="course_selector",
)
selected_ids = [course_id for name in selected_names for course_id in course_name_to_ids[name]]
selected_rows = [row for row in COURSES if row["course_id"] in selected_ids]

st.divider()
st.info(f"当前已选择 {len(selected_names)} 门课程，共 {len(selected_rows)} 条课程时段配置。")
with st.expander("📋 已选择课程名称", expanded=False):
    if selected_names:
        st.write("、".join(selected_names))
    else:
        st.write("暂无选中课程")

st.subheader("🔍 课程时段预览")
preview = [{
    "课程ID": row["course_id"], "课程名称": row["course_name"], "教师": row["teacher"],
    "地点": row["location"], "星期": row["weekday"],
    "时段": f'{row["start_time"]} - {row["end_time"]}', "周次": row["week_range"]
} for row in selected_rows]
st.dataframe(preview, width="stretch", hide_index=True)

HOLIDAYS = {date(2026, 10, day) for day in range(1, 8)}
ics_data = build_ics(selected_ids, HOLIDAYS) if selected_ids else None
st.download_button(
    "📥 下载 人大苏州金融专硕课表.ics",
    data=ics_data or b"",
    file_name="人大苏州金融专硕课表.ics",
    mime="text/calendar; charset=utf-8",
    type="primary",
    disabled=not selected_ids,
    width="stretch",
)
if not selected_ids:
    st.warning("请至少选择一门课程后再下载。")

st.markdown("""
### 使用说明
1. 在多选框中选择课程，或使用全选/取消全选按钮。
2. 核对课程名称和全部时段预览。
3. 点击下载按钮获得 `.ics` 文件并导入日历。
4. 所有课程默认课前 15 分钟提醒；2026 年 10 月 1—7 日的课程会自动跳过。
""")