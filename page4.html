var SmartCMSCalendar = function(calendarUrl, eventCalendarUrlPrefix, miniCalendarId, eventIconPositionIsTail, targetCategoryNo) {
  var weekdayName = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  var weekdayJPName = ['日曜', '月曜', '火曜', '水曜', '木曜', '金曜', '土曜'];
  var calendarCurrentDateTime = null;
  var calendarData = [];
  var initialHash = null;

  var MAX_SEARCH_COND_COOKIE_AGE = 60 * 60 * 24;

  this.updateCalendarData = function(calendarDataUrl) {
    updateCalendarData(calendarDataUrl);
  }

  this.init = function(calendarDataUrl) {
    var params = getCurrentQueryParams();
    var oldStateType = $('#calStateBlock input[name=type]:first').val();
    var oldStateDate = $('#calStateBlock input[name=date]:first').val();
    if (oldStateType && oldStateDate) {
      calendarCurrentDateTime = new Date(oldStateDate);
      toggleCalendar(parseInt(oldStateType));
    } else {
      var hash = window.location.hash;
      var hashDateMatch = hash.match(/calendar_date_(\d+)_(\d+)_(\d+)/);
      if (calendarCurrentDateTime != null) {
        // toggleCalendar(1);
      } else if (hashDateMatch) {
        calendarCurrentDateTime = new Date(parseInt(hashDateMatch[1]), parseInt(hashDateMatch[2]) - 1, parseInt(hashDateMatch[3]));
        toggleCalendar(SmartCMSCalendarCommon.CALENDAR_TYPE_DATE);
        initialHash = hash;
      } else if (params && ('year' in params) && ('month' in params)) {
        if ('day' in params) {
          calendarCurrentDateTime = new Date(parseInt(params['year']), parseInt(params['month']) - 1, parseInt(params['day']));
          toggleCalendar(SmartCMSCalendarCommon.CALENDAR_TYPE_DATE);
        } else {
          calendarCurrentDateTime = new Date(parseInt(params['year']), parseInt(params['month']) - 1, 1);
          toggleCalendar(SmartCMSCalendarCommon.CALENDAR_TYPE_LIST);
          var hashDayMatch = hash.match(/day=(\d+)/);
          if (hashDayMatch) {
            initialHash = 'calendar_list_' + parseInt(params['year']) + '_' + parseInt(params['month']) + '_' + parseInt(hashDayMatch[1]);
          }
        }
      } else {
        calendarCurrentDateTime = new Date();
        toggleCalendar(SmartCMSCalendarCommon.CALENDAR_TYPE_LIST);
      }
    }
    initSearchForms();

    $('.calGoCurrentMonth').unbind('click').click(function() {
      goCurrentMonth();
      updateCalendar();
    });

    $('.calGoPrevMonth').unbind('click').click(function() {
      goPrevMonth();
      updateCalendar();
    });

    $('.calGoNextMonth').unbind('click').click(function() {
      goNextMonth();
      updateCalendar();
    });

    $('#calListBlock .changeCalendarType').unbind('click').click(function() {
      toggleCalendar(SmartCMSCalendarCommon.CALENDAR_TYPE_GRID);
    });
    $('#calGridBlock .changeCalendarType').unbind('click').click(function() {
      toggleCalendar(SmartCMSCalendarCommon.CALENDAR_TYPE_LIST);
    });
    $('#calDateBlock .changeCalendarType').unbind('click').click(function() {
      toggleCalendar(SmartCMSCalendarCommon.CALENDAR_TYPE_GRID);
    });

    $('#formEventSearch [name=search]').unbind('click').click(function() {
      submitSearch();
    });

    $('#formEventSearch [name=reset]').unbind('click').click(function() {
      $('#formEventSearch [name=eventTypeNo]').val('');
      $('#formEventSearch .formEventFieldBox [name=eventFieldNoList]').prop('checked', false);
      $('#formEventSearch .formEventFieldBox .formEventSearchFieldList').css('display', 'none');
      $('#formEventSearch .formEventAreaBox [name=eventAreaNoList]').prop('checked', false);
      $('#formEventSearch [name=search-key-text]').val('');
      loadDefaultCalendar(calendarDataUrl);
    });

    if (params || !loadSearchCondCookie()) {
      loadDefaultCalendar(calendarDataUrl);
    }

    $('#formEventSearch #formEventSearchType').unbind('change').change(function() {
      onChangeEventType();
    });
  }

  this.initMiniCalendar = function(calendarDataUrl) {
    var oldStateDate = $('#miniCalendarStateBlock' + miniCalendarId + ' input[name=date]:first').val();
    calendarCurrentDateTime = oldStateDate ? new Date(oldStateDate) : new Date();
    $('#miniCalendarTable' + miniCalendarId + ' .miniCalGoCurrentMonth').unbind('click').click(function() {
      goCurrentMonth();
      updateMiniCalendar();
    });

    $('#miniCalendarTable' + miniCalendarId + ' .miniCalGoPrevMonth').unbind('click').click(function() {
      goPrevMonth();
      updateMiniCalendar();
    });

    $('#miniCalendarTable' + miniCalendarId + ' .miniCalGoNextMonth').unbind('click').click(function() {
      goNextMonth();
      updateMiniCalendar();
    });
    updateMiniCalendarData(calendarDataUrl);
  }

  function submitSearch() {
    var eventTypeNo = $('#formEventSearch [name=eventTypeNo]').val();
    var eventFieldNos = '';
    if (eventTypeNo) {
      eventFieldNos = $('#formEventSearch #formEventSearchFieldList_' + eventTypeNo + ' [name=eventFieldNoList]:checked').map(function(index, element) {
        return $(element).val()
      }).get().join(',');
    } else {
      eventTypeNo = '';
    }
    var eventAreaNos = $('#formEventSearch [name=eventAreaNoList]:checked').map(function(index, element) {
      return $(element).val()
    }).get().join(',');
    var keyword = $('#formEventSearch [name=search-key-text]').val();
    var eventCalendarUrl = eventCalendarUrlPrefix;
    eventCalendarUrl += '&eventTypeNo=' + encodeURIComponent(eventTypeNo);
    eventCalendarUrl += '&eventFieldNo=' + encodeURIComponent(eventFieldNos);
    eventCalendarUrl += '&eventAreaNo=' + encodeURIComponent(eventAreaNos);
    eventCalendarUrl += '&keyword=' + encodeURIComponent(keyword);
    eventCalendarUrl += '&timeSpanType=-1';
    $('#eventCalendarSearchBox').css('display', '');
    saveSearchCondCookie(eventTypeNo, eventFieldNos, eventAreaNos, keyword);
    updateCalendarData(eventCalendarUrl);
  }

  function updateEventCalendarByParams(eventTypeNo, eventFieldNos, eventAreaNos, keyword, fromDate, toDate) {
    var eventCalendarUrlSuffix = '';
    if (eventTypeNo) {
      $('#formEventSearch [name=eventTypeNo]').val(eventTypeNo);
      onChangeEventType();
      eventCalendarUrlSuffix += '&eventTypeNo=' + encodeURIComponent(eventTypeNo);
    }
    if (eventFieldNos) {
      eventFieldNos.split(',').forEach(function(value, i, list) {
        $('#formEventSearch input#eventFieldNoList_' + parseInt(value)).prop('checked', true);
      });
      eventCalendarUrlSuffix += '&eventFieldNo=' + encodeURIComponent(eventFieldNos);
    }
    if (eventAreaNos) {
      eventAreaNos.split(',').forEach(function(value, i, list) {
        $('#formEventSearch input#eventAreaNoList_' + parseInt(value)).prop('checked', true);
      });
      eventCalendarUrlSuffix += '&eventAreaNo=' + encodeURIComponent(eventAreaNos);
    }
    if (keyword) {
      $('#formEventSearch [name=search-key-text]').val(keyword);
      eventCalendarUrlSuffix += '&keyword=' + encodeURIComponent(keyword);
    }
    if (fromDate) {
      eventCalendarUrlSuffix += '&fromDate=' + encodeURIComponent(fromDate);
    }
    if (toDate) {
      eventCalendarUrlSuffix += '&toDate=' + encodeURIComponent(toDate);
    }
    updateCalendarData(eventCalendarUrlPrefix + eventCalendarUrlSuffix + '&timeSpanType=-1');
  }

  function saveSearchCondCookie(eventTypeNo, eventFieldNos, eventAreaNos, keyword) {
    document.cookie = 'calendar_search_' + targetCategoryNo + '=' + eventTypeNo + '|' + eventFieldNos + '|' + eventAreaNos + '|' + encodeURIComponent(keyword) + ';max-age='
        + MAX_SEARCH_COND_COOKIE_AGE;
  }

  function loadSearchCondCookie() {
    var params = document.cookie.split(';');
    for (var i = 0; i < params.length; i++) {
      var element = params[i].split('=');
      if (element.length >= 2) {
        var name = decodeURIComponent(element[0].replace(/^\s+|\s+$/g, ''));
        var value = decodeURIComponent(element[1].replace(/^\s+|\s+$/g, ''));
        if (name == 'calendar_search_' + targetCategoryNo) {
          var values = value.split('|');
          if (values.length >= 4) {
            updateEventCalendarByParams(values[0], values[1], values[2], values[3], null, null);
          }
          return true;
        }
      }
    }
    return false;
  }
  function loadDefaultCalendar(calendarDataUrl) {
    var params = getCurrentQueryParams();
    // var isEventSearch = params ? true : false;
    var isEventSearch = false;
    if (params && ('calendarType' in params)) {
      isEventSearch = false;
      toggleCalendar(params['calendarType']);
    }

    if (params) {
      var eventTypeNo = null;
      var eventFieldNos = null;
      var eventAreaNos = null;
      var keyword = null;
      var fromDate = null;
      var toDate = null;
      if ('eventTypeNo' in params) {
        eventTypeNo = params['eventTypeNo'];
        isEventSearch = true;
      }
      if ('eventFieldNo' in params) {
        eventFieldNos = params['eventFieldNo'];
        isEventSearch = true;
      }
      if ('eventAreaNo' in params) {
        eventAreaNos = params['eventAreaNo'];
        isEventSearch = true;
      }
      if ('keyword' in params) {
        keyword = params['keyword'];
        isEventSearch = true;
      }
      if ('fromDate' in params) {
        fromDate = encodeURIComponent(params['fromDate']);
        isEventSearch = true;
      }
      if ('toDate' in params) {
        toDate = encodeURIComponent(params['toDate']);
        isEventSearch = true;
      }
    }
    if (isEventSearch) {
      $('#eventCalendarSearchBox').css('display', '');
      updateEventCalendarByParams(eventTypeNo, eventFieldNos, eventAreaNos, keyword, fromDate, toDate);
    } else {
      $('#eventCalendarSearchBox').css('display', 'none');
      updateCalendarData(calendarDataUrl);
    }
  }
  function onChangeEventType() {
    var val = $('#formEventSearch #formEventSearchType option:selected').val();
    $('#formEventSearch .formEventSearchFieldList').css('display', 'none');
    if (val) {
      $('#formEventSearch #formEventSearchFieldList_' + val).css('display', '');
      $('#formEventSearch .formEventFieldBox').css('display', '');
    } else {
      $('#formEventSearch .formEventFieldBox').css('display', 'none');
    }
  }

  function updateCalendarData(calendarDataUrl) {
    SmartCMSCalendarCommon.showLoadingDialog();
    $.getJSON(calendarDataUrl, function(json) {
      calendarData = json;
      updateCalendar();
      SmartCMSCalendarCommon.hideLoadingDialog();
    });
  }

  function updateMiniCalendarData(calendarDataUrl) {
    $.getJSON(calendarDataUrl, function(json) {
      calendarData = json;
      updateMiniCalendar();
    });
  }

  function getCurrentQueryParams() {
    var search = window.location.search;
    if (search.length <= 1) {
      return false;
    }
    var query = window.location.search.substring(1);
    var params = query.split('&');
    var result = new Object();
    for (var i = 0; i < params.length; i++) {
      var element = params[i].split('=');
      var name = decodeURIComponent(element[0]);
      result[name] = decodeURIComponent(element[1]);
    }
    return result;
  }

  function initSearchForms() {
    var search = window.location.search;
    if (search.length <= 1) {
      return false;
    }
    var query = window.location.search.substring(1);
    var params = query.split('&');
    var result = new Object();
    $('#formEventSearchType option').attr('data-show-type-option', '1');
    for (var i = 0; i < params.length; i++) {
      var element = params[i].split('=');
      var name = decodeURIComponent(element[0]);
      var value = decodeURIComponent(element[1]);
      var values = value.split(',');
      switch (name) {
        case 'type-display':
          $('#formEventSearch .formEventTypeBox').css('display', ((value == 0) ? 'none' : 'block'));
          // fall through
        case 'field-display':
          $('#formEventSearch .formEventFieldBox').css('display', ((value == 0) ? 'none' : 'block'));
          break;
        case 'area-display':
          $('#formEventSearch .formEventAreaBox').css('display', ((value == 0) ? 'none' : 'block'));
          break;
        case 'type-option-display':
          if (values.length > 0) {
            $('#formEventSearchType option').attr('data-show-type-option', '0');
            $('#formEventSearchType option[value=]').attr('data-show-type-option', '1');
            $.each(values, function(index, val) {
              $('#formEventSearchType option[value=' + val + ']').attr('data-show-type-option', '1');
            });
          }
          break;
        case 'type-option-non-display':
          if (values.length > 0) {
            $.each(values, function(index, val) {
              $('#formEventSearchType option[value=' + val + ']').attr('data-show-type-option', '0');
            });
          }
          break;
        case 'field-option-display':
          if (values.length > 0) {
            $('#formEventSearch .formEventSearchFieldList .eventFieldItem').hide();
            $.each(values, function(index, val) {
              $('#formEventSearch .formEventSearchFieldList .eventFieldItem_' + val).show();
            });
          }
          break;
        case 'field-option-non-display':
          if (values.length > 0) {
            $.each(values, function(index, val) {
              $('#formEventSearch .formEventSearchFieldList .eventFieldItem_' + val).hide();
            });
          }
          break;
        case 'area-option-display':
          if (values.length > 0) {
            $('#formEventSearch .formEventAreaBox .eventAreaItem').hide();
            $.each(values, function(index, val) {
              $('#formEventSearch .formEventAreaBox .eventAreaItem_' + val).show();
            });
          }
          break;
        case 'area-option-non-display':
          if (values.length > 0) {
            $.each(values, function(index, val) {
              $('#formEventSearch .formEventAreaBox .eventAreaItem_' + val).hide();
            });
          }
          break;
      }
    }
    $('#formEventSearchType option[data-show-type-option=0]').remove();
    $('#formEventSearchType option').removeAttr('data-show-type-option');
  }

  function goCurrentMonth() {
    calendarCurrentDateTime = new Date();
  }

  function goPrevMonth() {
    var year = calendarCurrentDateTime.getFullYear();
    var month = calendarCurrentDateTime.getMonth() + 1;
    calendarCurrentDateTime = SmartCMSCalendarCommon.getPrevMonthDate(year, month);
  }

  function goNextMonth() {
    var year = calendarCurrentDateTime.getFullYear();
    var month = calendarCurrentDateTime.getMonth() + 1;
    calendarCurrentDateTime = SmartCMSCalendarCommon.getNextMonthDate(year, month);
  }

  function toggleCalendar(mode) {
    switch (parseInt(mode)) {
      case SmartCMSCalendarCommon.CALENDAR_TYPE_GRID:
        $('#calDateBlock').css('display', 'none');
        $('#calGridBlock').css('display', 'block');
        $('#calListBlock').css('display', 'none');
        break;
      case SmartCMSCalendarCommon.CALENDAR_TYPE_DATE:
        $('#calDateBlock').css('display', 'block');
        $('#calGridBlock').css('display', 'none');
        $('#calListBlock').css('display', 'none');
        break;
      default:
        $('#calDateBlock').css('display', 'none');
        $('#calGridBlock').css('display', 'none');
        $('#calListBlock').css('display', 'block');
        break;
    }
    $('#calStateBlock input[name=type]:first').val(mode);
  }

  function updateCalendar() {
    $('#calStateBlock input[name=date]:first').val(calendarCurrentDateTime.toDateString());
    var currentYear = calendarCurrentDateTime.getFullYear();
    var currentMonth = calendarCurrentDateTime.getMonth() + 1;
    var currentMday = calendarCurrentDateTime.getDate();
    var currentWday = new Date(currentYear, currentMonth - 1, currentMday).getDay();

    var todayDateTime = new Date();
    var todayYear = todayDateTime.getFullYear();
    var todayMonth = todayDateTime.getMonth() + 1;
    var todayMday = todayDateTime.getDate();

    var yearHeisei = currentYear - 1988;
    $('.calendarYearAD').text(currentYear);
    $('.calendarYearJPPrefix').text(SmartCMSCalendarCommon.getJPYearPrefix(currentYear, currentMonth));
    $('.calendarYearJP').text(SmartCMSCalendarCommon.getJPYear(currentYear, currentMonth));
    $('.calendarMonth').text(currentMonth);
    $('.calendarDate').text(currentMday);

    $('.calGridRow').remove();

    // create grid
    var gridTable = $('#calGridTable');
    var gridDataList = createGridDataList(currentYear, currentMonth);

    var topWday = new Date(currentYear, currentMonth - 1, 1).getDay();
    var firstGridMday = -topWday + 1;
    var lastMday = SmartCMSCalendarCommon.getMonthLastMday(currentYear, currentMonth);
    var lastWday = new Date(currentYear, currentMonth - 1, lastMday).getDay();
    var lastGridMday = lastMday - lastWday + 6;

    var processList = {};
    for (var i = firstGridMday; i <= lastGridMday; i++) {
      processList[i] = 0;
    }
    for (var sunMday = firstGridMday; sunMday <= lastGridMday; sunMday += 7) {
      var headerGirdRow = $('<tr class="col-day calGridRow"><\/tr>');
      for (var wday = 0; wday < 7; wday++) {
        i = sunMday + wday;
        var gridData = gridDataList[i];
        var td = '<td';
        if (gridData['cls']) {
          td += ' class="' + gridData['cls'] + '"';
        }
        td += '>';
        if (i <= 0) {
          td += '<p class="prevMonthDate">';
        } else if (i > lastMday) {
          td += '<p class="nextMonthDate">';
        } else {
          td += '<p>';
        }
        td += gridData['mday'];
        if (gridData['holiday']) {
          td += ' <span class="holidayName">' + gridData['holiday'] + '<\/span>';
        }
        td += '<\/p><\/td>';
        headerGirdRow.append(td);
      }
      gridTable.append(headerGirdRow);

      while (true) {
        var eventCount = 0;
        var currentGirdRow = $('<tr class="col calGridRow"><\/tr>');
        for (var wday = 0; wday < 7; wday++) {
          i = sunMday + wday;
          var gridData = gridDataList[i];
          var cls = gridData['cls'] ? gridData['cls'] : '';

          var eventList = gridData['events'];

          var eventFound = false;
          for (var j = processList[i]; j < eventList.length; j++) {
            var event = eventList[j];
            var continuous = event['continuous'];
            var span = event['span'];
            var stepover = (7 - wday < span);
            if (stepover) {
              span = 7 - wday;
            }

            if (wday == 0 || !continuous) {
              var beginWday = wday;
              var td = '<td';
              if (span > 1) {
                td += ' colspan="' + span + '"';
                wday += span - 1;
              }
              td += '>';
              var eventTag = createEventLinkTag(event, false, false);

              if (beginWday == 0 && continuous) {
                if (stepover) {
                  eventTag = '<p class="step_over_end step_over_next ' + event['event_apply_class'] + '">' + eventTag + '<\/p>';
                } else {
                  eventTag = '<p class="step_over_end ' + event['event_apply_class'] + '">' + eventTag + '<\/p>';
                }
              } else if (stepover) {
                eventTag = '<p class="step_over_next ' + event['event_apply_class'] + '">' + eventTag + '<\/p>';
              } else {
                eventTag = '<p class="' + event['event_apply_class'] + '">' + eventTag + '<\/p>';
              }
              currentGirdRow.append(td + eventTag + '<\/td>');
              processList[i] = j + 1;
              eventFound = true;
              eventCount++;
              break;
            }
          }
          if (!eventFound) {
            var td = '<td class="' + cls + '">';
            currentGirdRow.append(td);
          }
        }
        if (eventCount == 0) {
          break;
        }
        gridTable.append(currentGirdRow);
      }
    }

    // create list
    $('.calListRow').remove();
    var listTable = $('#calListTable');
    for (var mday = 1; mday <= lastMday; mday++) {
      var wday = new Date(currentYear, currentMonth - 1, mday).getDay();
      var holiday = SmartCMSCalendarCommon.getHolidayName(currentYear, currentMonth, mday);
      var dayClass = weekdayName[wday];
      if (holiday) {
        // dayClass = 'Holiday';
        dayClass = 'sun';
      } else if (todayYear == currentYear && todayMonth == currentMonth && todayMday == mday) {
        // dayClass = 'Today';
      }

      var detail = '';
      var eventList = getDailyEventList(currentYear, currentMonth, mday);
      if (eventList) {
        for (var i = 0; i < eventList.length; i++) {
          var event = eventList[i];
          detail += createEventLinkTag(event, true, true);
        }
      }

      if (holiday) {
        listTable.append('<tr class="calListRow calListWeekday ' + dayClass + '"><td id="calendar_list_' + currentYear + '_' + currentMonth + '_' + mday + '" class="date">' + mday + '<\/td><td>'
            + weekdayJPName[wday] + '<\/td><td>' + holiday + detail + '<\/td><\/tr>');
      } else {
        listTable.append('<tr class="calListRow calListWeekday ' + dayClass + '"><td id="calendar_list_' + currentYear + '_' + currentMonth + '_' + mday + '" class="date">' + mday + '<\/td><td>'
            + weekdayJPName[wday] + '<\/td><td>' + detail + '<\/td><\/tr>');
      }
    }

    // create date : TODO デザインどうするか
    $('.calDateRow').remove();
    var dateTable = $('#calDateTable');
    var detail = '';
    var eventList = getDailyEventList(currentYear, currentMonth, currentMday);
    if (eventList) {
      for (var i = 0; i < eventList.length; i++) {
        var event = eventList[i];
        detail += createEventLinkTag(event, true, false);
      }
    }
    dateTable.append('<tr class="calListRow calListWeekday"><td>' + detail + '<\/td><\/tr>');

    // create event list
    updateEventApplyListTable('ApplySoon', getEventApplyList(SmartCMSCalendarCommon.EVENT_APPLY_STATUS_FINISH_SOON));
    updateEventApplyListTable('ApplyRecently', getEventApplyList(SmartCMSCalendarCommon.EVENT_APPLY_STATUS_FINISHED_RECENTLY));

    jumpInitialHash();
  }

  function updateEventApplyListTable(tag, eventList) {
    $('.calEvent' + tag + 'Item').remove();
    var eventApplyList = $('#calEvent' + tag + 'List');
    var limit = eventApplyList.attr('data-limit');
    if (eventList && eventList.length > 0) {
      for (var i = 0; i < eventList.length; i++) {
        var event = eventList[i];
        var applyEndDateString = SmartCMSCalendarCommon.convertSqlDateTimeToJpString(event.event['event_apply_end_datetime']);
        eventApplyList.append('<li><div class="calEvent' + tag + 'Item calEvent' + tag + 'ItemHead"><a href="' + event['url'] + '">' + event['page_name'] + '<\/a><\/div>' + '<dl class="calEvent'
            + tag + 'Item calEvent' + tag + 'ItemBody"><dt>【申し込み締切日】<\/dt><dd>' + applyEndDateString + '<\/dd><\/dl><\/li>');
        if (limit != 0 && i >= limit - 1) {
          break;
        }
      }
      $('#calEvent' + tag + 'Block').css('display', '');
      $('.calEvent' + tag + 'Link').css('display', '');
    } else {
      $('#calEvent' + tag + 'Block').css('display', 'none');
      $('.calEvent' + tag + 'Link').css('display', 'none');
    }
  }

  function updateMiniCalendar() {
    $('#miniCalendarStateBlock' + miniCalendarId + ' input[name=date]:first').val(calendarCurrentDateTime.toDateString());
    var year = calendarCurrentDateTime.getFullYear();
    var month = calendarCurrentDateTime.getMonth() + 1;

    var todayDateTime = new Date();
    var todayYear = todayDateTime.getFullYear();
    var todayMonth = todayDateTime.getMonth() + 1;
    var todayMday = todayDateTime.getDate();

    $('#miniCalendarTable' + miniCalendarId + ' .miniCalendarYearAD').text(year);
    $('#miniCalendarTable' + miniCalendarId + ' .miniCalendarYearJPPrefix').text(SmartCMSCalendarCommon.getJPYearPrefix(year, month));
    $('#miniCalendarTable' + miniCalendarId + ' .miniCalendarYearJP').text(SmartCMSCalendarCommon.getJPYear(year, month));
    $('#miniCalendarTable' + miniCalendarId + ' .miniCalendarMonth').text(month);

    $('#miniCalendarTable' + miniCalendarId + ' .miniCalGridRow').remove();

    var gridTable = $('#miniCalendarTable' + miniCalendarId + ' .miniCalGridTable');

    var topWday = new Date(year, month - 1, 1).getDay();
    var firstGridMday = -topWday + 1;
    var lastMday = SmartCMSCalendarCommon.getMonthLastMday(year, month);
    var lastWday = new Date(year, month - 1, lastMday).getDay();
    var lastGridMday = lastMday - lastWday + 6;

    for (var sunMday = firstGridMday; sunMday <= lastGridMday; sunMday += 7) {
      var headerGirdRow = $('<tr class="col-day miniCalGridRow"><\/tr>');
      for (var wday = 0; wday < 7; wday++) {
        i = sunMday + wday;
        var datetime = new Date(year, month - 1, i);
        var year0 = datetime.getFullYear();
        var month0 = datetime.getMonth() + 1;
        var mday0 = datetime.getDate();
        var holiday = SmartCMSCalendarCommon.getHolidayName(year, month, i);
        var td = '<td';
        if (holiday) {
          td += ' class="day-sun holiday"';// FIXME
        }
        td += '>';
        if (i <= 0) {
          td += '<p class="prevMonthDate">';
        } else if (i > lastMday) {
          td += '<p class="nextMonthDate">';
        } else {
          td += '<p>';
        }
        var eventList = getDailyEventList(year0, month0, mday0);
        // if (eventList.length == 1) {
        // td += '<a href="' + eventList[0]['url'] + '"><span>' + mday0 +
        // '<\/span><\/a>';
        // } else
        if (eventList.length > 0) {
          td += '<a href="' + calendarUrl + '#calendar_date_' + year0 + '_' + month0 + '_' + mday0 + '"><span>' + mday0 + '<\/span><\/a>';
        } else {
          td += mday0;
        }
        td += '<\/p><\/td>';
        headerGirdRow.append(td);
      }
      gridTable.append(headerGirdRow);
    }
  }
  function createGridDataList(year, month) {
    var result = {};

    var curLastMday = SmartCMSCalendarCommon.getMonthLastMday(year, month);
    var prev = SmartCMSCalendarCommon.getPrevMonthDate(year, month);
    var prevLastMday = SmartCMSCalendarCommon.getMonthLastMday(prev.getFullYear(), prev.getMonth() + 1);
    var next = SmartCMSCalendarCommon.getNextMonthDate(year, month);
    var nextLastMday = SmartCMSCalendarCommon.getMonthLastMday(next.getFullYear(), next.getMonth() + 1);

    for (var i = 1; i <= prevLastMday; i++) {
      result[i - prevLastMday] = createGridDataNode(prev.getFullYear(), prev.getMonth() + 1, i);
    }

    for (var i = 1; i <= curLastMday; i++) {
      result[i] = createGridDataNode(year, month, i);
    }

    for (var i = 1; i <= nextLastMday; i++) {
      result[i + curLastMday] = createGridDataNode(next.getFullYear(), next.getMonth() + 1, i);
    }
    return result;
  }

  function createGridDataNode(year, month, mday) {
    var wday = new Date(year, month - 1, mday).getDay();
    var holiday = SmartCMSCalendarCommon.getHolidayName(year, month, mday);
    var cls = false;
    if (holiday) {
      cls = 'day-sun holiday'; // FIXME
    } else if (wday == 0) {
      cls = 'day-sun';
    } else if (wday == 6) {
      cls = 'day-sat';
    }
    return {
      'year': year,
      'month': month,
      'mday': mday,
      'events': getDailyEventList(year, month, mday),
      'holiday': holiday,
      'cls': cls
    };
  }

  function createEventLinkTag(event, enableDivTag, enableTextTags) {
    var linkTag = '<a href="' + event['url'] + '">' + event['page_name'] + '<\/a>';
    var textIcons = '';
    if (event.event && 'event_fields' in event.event) {
      $.each(event.event.event_fields, function(field_no, field_name) {
        textIcons += '<span class="event_icon event_field' + field_no + '">' + field_name + '</span>';
      });
    }
    if (event.event && 'event_area' in event.event) {
      $.each(event.event.event_area, function(area_no, area_name) {
        textIcons += '<span class="event_icon event_area' + area_no + '">' + area_name + '</span>';
      });
    }
    if (enableDivTag) {
      if (enableTextTags && textIcons.length > 0) {
        result = '<div class="calPageLink is-tag ' + event['event_apply_class'] + '">';
        if (eventIconPositionIsTail) {
          result += linkTag + textIcons;
        } else {
          result += textIcons + linkTag;
        }
        result += '<\/div>';
      } else {
        result = '<div class="calPageLink ' + event['event_apply_class'] + '">' + linkTag + '<\/div>';
      }
    } else {
      result = linkTag;
    }
    return result;
  }

  function jumpInitialHash() {
    if (initialHash) {
      window.location.hash = "#";
      window.location.hash = initialHash;
      initialHash = null;
    }
  }

  function getDailyEventList(year, month, mday) {
    var dateString = SmartCMSCalendarCommon.createDateString(year, month, mday);
    var result = [];
    for (var i = 0; i < calendarData.length; i++) {
      var event = calendarData[i];
      for (var j = 0; j < event.date_list.length; j++) {
        var start = event.date_list[j][0];
        var end = event.date_list[j][1];
        if (start <= dateString && dateString <= end) {
          result.push(createObjectByEvent(event, (dateString != start), SmartCMSCalendarCommon.getDateDiff(dateString, end) + 1));
          break;
        }
      }
    }
    return result;
  }

  function getEventApplyList($eventApplyStatus) {
    var result = [];
    for (var i = 0; i < calendarData.length; i++) {
      var event = calendarData[i];
      if ('event' in event && event.event != null && event.event['event_apply_status_list_display'] && event.event['event_apply_status'] == $eventApplyStatus) {
        result.push(createObjectByEvent(event, false, 1));
      }
    }
    result.sort(function(a, b) {
      if (a.event['event_apply_end_datetime'] < b.event['event_apply_end_datetime']) {
        return -1;
      } else if (a.event['event_apply_end_datetime'] > b.event['event_apply_end_datetime']) {
        return 1;
      } else {
        return 0;
      }
    });
    return result;
  }

  function createObjectByEvent(event, continuous, span) {
    var pageNo = event.page_no;
    var pageName = event.page_name;
    var pageUrl = event.url;
    if (pageNo <= 0) {
      pageUrl += '?ref=' + window.location.href;
    }
    return {
      page_no: pageNo,
      page_name: pageName,
      url: pageUrl,
      continuous: continuous,
      span: span,
      event: ('event' in event) ? event.event : null,
      event_apply_class: getEventApplyClassName(event)
    };
  }

  function getEventApplyClassName(event) {
    var eventApplyClassName = 'event_apply_status_none';
    if ('event' in event && event.event != null && event.event['event_apply_status_icon_display']) {
      switch (event.event['event_apply_status']) {
        case SmartCMSCalendarCommon.EVENT_APPLY_STATUS_UPCOMING:
          eventApplyClassName = 'event_apply_status_upcoming';
          break;
        case SmartCMSCalendarCommon.EVENT_APPLY_STATUS_WANTED:
          eventApplyClassName = 'event_apply_status_wanted';
          break;
        case SmartCMSCalendarCommon.EVENT_APPLY_STATUS_FINISH_SOON:
          eventApplyClassName = 'event_apply_status_finish_soon';
          break;
        case SmartCMSCalendarCommon.EVENT_APPLY_STATUS_FINISHED_RECENTLY:
          eventApplyClassName = 'event_apply_status_finished_recently';
          break;
        case SmartCMSCalendarCommon.EVENT_APPLY_STATUS_FINISHED:
          eventApplyClassName = 'event_apply_status_finished';
          break;
      }
      if (event.event['event_apply_status_icon_position'] == 1) {
        eventApplyClassName += '_after';
      } else {
        eventApplyClassName += '_before';
      }
    }
    return eventApplyClassName;
  }
};
