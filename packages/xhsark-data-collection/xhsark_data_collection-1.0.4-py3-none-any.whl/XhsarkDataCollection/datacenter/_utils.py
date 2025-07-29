from time import sleep

from DrissionPage._pages.mix_tab import MixTab


def pick__daterange(page: MixTab, begin_date: str, end_date: str):
    """
    选择自定义日期范围

    Args:
        begin_date: 起始日期, YYYY-MM-DD
        end_date: 结束日期, YYYY-MM-DD
    """

    trigger_btn = page.ele('t:button@@text()=自定义', timeout=3)
    if not trigger_btn:
        raise RuntimeError('未找到自定义日期范围按钮')
    trigger_btn = trigger_btn.parent()

    trigger_btn.set.style('position', 'fixed')
    trigger_btn.set.style('top', 0)
    trigger_btn.set.style('left', 0)
    trigger_btn.set.style('zIndex', 1001)

    for _ in range(3):
        sleep(0.5)
        trigger_btn.click()
        popup_container = trigger_btn.ele('c:div[data-popper-placement]', timeout=3)
        if popup_container:
            break
    else:
        raise RuntimeError('未找到日期选择器弹出层元素')

    year_btn_eles = popup_container.eles('x://div[contains(text(), " 年")]', timeout=1)
    if not year_btn_eles:
        raise RuntimeError('日期选择器中未找到 [年份] 切换按钮')

    # 分割传入的日期
    daterange_split = list(map(lambda x: x.split('-'), [begin_date, end_date]))

    # 判断年份
    for i, (year, month, _) in enumerate(daterange_split):
        if year == year_btn_eles[i].text[:-2]:
            continue
        sleep(0.5)

        year_btn_eles[i].click(by_js=True)
        target_year_btn = popup_container.ele(
            f't:div@@class=calendar-matrixCell@@text()={year}', timeout=2
        )
        if not target_year_btn:
            raise RuntimeError(f'日期选择器中未找到年份 [{year}]')
        if target_year_btn.attr('data-disabled') == 'true':
            raise RuntimeError(f'年份 [{year}] 禁止选择, 请检查')
        target_year_btn.click(by_js=True)
        sleep(0.5)

        # 修改完年份之后必须要选择月份
        month_noprefix = month.lstrip('0')
        target_month_btn = popup_container.ele(
            f't:div@@class=calendar-matrixCell@@text()={month_noprefix}月', timeout=2
        )
        if not target_month_btn:
            raise RuntimeError(f'选择年份之后未找到对应的月份 [{month_noprefix}月]')
        target_month_btn.click(by_js=True)
        sleep(0.5)

    # 判断月份
    month_btn_eles = popup_container.eles('x://div[contains(text(), " 月")]', timeout=1)
    if not month_btn_eles:
        raise RuntimeError('日期选择器中未找到 [月份] 切换按钮')
    for i, (_, month, _) in enumerate(daterange_split):
        month_noprefix = month.lstrip('0')
        if month == month_btn_eles[i].text[:-2]:
            continue
        sleep(0.5)

        month_btn_eles[i].click(by_js=True)
        target_month_btn = popup_container.ele(
            f't:div@@class=calendar-matrixCell@@text()={month_noprefix}月', timeout=2
        )
        if not target_month_btn:
            raise RuntimeError(f'日期选择器中未找到月份 [{month_noprefix}月]')
        if target_month_btn.attr('data-disabled') == 'true':
            raise RuntimeError(f'月份 [{month_noprefix}月] 禁止选择, 请检查')
        target_month_btn.click(by_js=True)
        sleep(0.5)

    # 选择对应日期
    day_panel_eles = popup_container.eles('c:div[data-calendar="body"]', timeout=2)
    if not day_panel_eles:
        raise RuntimeError('日期选择器中未找到日期面板')
    month_btn_eles = popup_container.eles('x://div[contains(text(), " 月")]', timeout=1)
    for i in range(2):
        for year, month, day in daterange_split:
            if month != month_btn_eles[i].text[:-2]:
                break

            day_noprefix = day.lstrip('0')
            target_day_panel = day_panel_eles[i]
            target_day_btn = target_day_panel.ele(
                f't:div@@class=calendar-dayCell@@text()={day_noprefix}', timeout=1
            )

            date = f'{year}-{month}-{day}'
            if not target_day_btn:
                raise RuntimeError(f'日期选择器中未找到 [{date}] 按钮')
            if target_day_btn.attr('data-disabled') == 'true':
                raise RuntimeError(f'目标日期 [{date}] 禁止选择, 请检查')
            target_day_btn.click(by_js=True)
            sleep(0.5)
