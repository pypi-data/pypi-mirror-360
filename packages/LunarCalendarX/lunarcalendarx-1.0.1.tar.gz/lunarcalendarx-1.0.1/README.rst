LunarCalendarX: A Lunar-Solar Converter
=======================================

.. image::
  https://img.shields.io/pypi/v/LunarCalendarX.svg
  :target: https://pypi.python.org/pypi/LunarCalendarX
  :alt: Last stable version (PyPI)

.. image::
  https://github.com/chengchang/LunarCalendarX/actions/workflows/tests.yml/badge.svg
  :target: https://github.com/chengchang/LunarCalendarX/actions/workflows/tests.yml
  :alt: build status

**Note**: This library is a fork of `LunarCalendar <https://github.com/wolfhong/LunarCalendar>`_ and is maintained as a continuation of the original project.


Overview
--------

`Chinese version(中文版) <https://github.com/chengchang/LunarCalendarX/blob/master/README_zh.rst>`_ is provided.

LunarCalendarX is a Lunar-Solar Converter, containing a number of lunar and solar festivals in China.

Korean, Japanese or Vietnamese lunar calendar is the same as Chinese calendar, but has different festivals.
Korean, Japanese and Vietnamese festivals can be easily included, with their languages.

LunarCalendarX supports a time range of 1900 to 2100, which may be enough for a long time.
But if you have needs for a wider time range, you can use ``generate.html`` to extend it.

LunarCalendarX is inspired by `Lunar-Solar-Calendar-Converter <https://github.com/isee15/Lunar-Solar-Calendar-Converter>`_.


Features
--------

* Accurate raw data, synchronize with Microsolf's ``ChineseLunisolarCalendar`` class
* Easy to extend festivals and languages, supported both ``zh_hans`` and ``zh_hant``
* Included Lunar Festivals, such as: MidAutumn Festival, Chinese New Year Eve, DragonBoat Festivals
* Included Solar Festivals without fixed dates, such as: Mother's Day, Easter
* Added legality check of the lunar and solar date
* Supported 24 solar terms(立春/春分/清明/冬至等)


Install
-------

LunarCalendarX can be installed from the PyPI with ``pip``::

   $ pip install LunarCalendarX

If you encounter an error like ``command 'gcc' failed with exit status 1 while installing ephem``, maybe you should install ``python-devel`` first.
For CentOS::

   $ yum install python-devel

For Ubuntu::

   $ apt-get install python-dev

For Windows, maybe you should install `Microsoft Build Tools <https://www.microsoft.com/en-us/download/details.aspx?id=48159>`_ first. It will help you building c++ code for ``ephem`` library, which LunarCalendarX includes for 24-solar-terms calculation.


Console Commands
----------------

A console command called ``lunar-find`` can be used to find the date of the festival, using it's chinese name.
Default to this year. Supporting alias of the festival.

.. code-block:: console

    $ lunar-find 重阳
    重阳节 on 2018: 2018-10-17

    $ lunar-find 重陽節
    重阳节 on 2018: 2018-10-17

    $ lunar-find 登高节 2019
    重阳节 on 2019: 2019-10-07

You can also print all included festivals or 24 solar terms by date asc with:

.. code-block:: console

    $ lunar-find all 2019
    $ lunar-find festival 2012
    $ lunar-find 节日 2012
    $ lunar-find solarterm
    $ lunar-find 节气


Quickstart
----------

Solar to Lunar:

.. code-block:: python

    import datetime
    from lunarcalendarx import Converter, Solar, Lunar, DateNotExist

    solar = Solar(2018, 1, 1)
    print(solar)
    lunar = Converter.Solar2Lunar(solar)
    print(lunar)
    solar = Converter.Lunar2Solar(lunar)
    print(solar)
    print(solar.to_date(), type(solar.to_date()))

Lunar to Solar:

.. code-block:: python

    lunar = Lunar(2018, 2, 30, isleap=False)
    print(lunar)
    solar = Converter.Lunar2Solar(lunar)
    print(solar)
    lunar = Converter.Solar2Lunar(solar)
    print(lunar)
    print(lunar.to_date(), type(lunar.to_date()))
    print(Lunar.from_date(datetime.date(2018, 4, 15)))

Legality check for solar and lunar date. 2018-2-15(Leap Month) does not exist, but 2012-4-4(Leap Month) exists:

.. code-block:: python

    Lunar(2012, 4, 4, isleap=True)  # date(2012, 5, 24)
    try:
        lunar = Lunar(2018, 2, 15, isleap=True)
    except DateNotExist:
        print(traceback.format_exc())

Print all the festivals included, with Chinese and English. Other languages are welcome to extend(Fork & Pull Request).

.. code-block:: python

    from lunarcalendarx.festival import festivals

    # print festivals, using English or Chinese
    print("----- print all festivals on 2018 in chinese: -----")
    for fest in festivals:
        print(fest.get_lang('zh'), fest(2018))

    print("----- print all festivals on 2017 in english: -----")
    for fest in festivals:
        print(fest.get_lang('en'), fest(2017))

Output:

.. code-block:: shell

    ......
    母亲节 2018-05-13
    父亲节 2018-06-17
    中秋节 2018-09-24
    感恩节 2018-11-22
    重阳节 2018-10-17
    春节 2018-02-16
    中元节 2018-08-25
    七夕节 2018-08-17
    腊八节 2019-01-13
    清明节 2018-04-05
    除夕 2019-02-04
    寒衣节 2018-11-08
    元宵节 2018-03-02
    龙抬头 2018-03-18
    端午节 2018-06-18
    ......


Contribution
------------

Including festival standards:

* Common festivals in the the country, such as: Christmas, Halloween, etc.
* Lunar festivals.
* Solar festivals without fixed dates, such as: Mother's Day, Easter, etc.

Supporting Chinese and English only now. If you want to add Korean, Japanese or Vietnamese supports, modify ``lunarcalendarx/festival.py`` to add festivals and languages.

Some unusual festivals may not be included, `welcome to extend <https://github.com/wolfhong/LunarCalendar/issues>`_.



About
-----

* `Homepage <https://github.com/chengchang/LunarCalendarX>`_
* `PyPI <https://pypi.python.org/pypi/LunarCalendarX>`_
* `Issue tracker <https://github.com/chengchang/LunarCalendarX/issues?status=new&status=open>`_
* `Original project <https://github.com/wolfhong/LunarCalendar>`_
