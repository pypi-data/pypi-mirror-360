





def get_base_info(stock_codes):
    """
    Parameters
    ----------
    stock_codes : Union[str, List[str]]
        股票代码或股票代码构成的列表

    Returns
    -------
    Union[Series, DataFrame]

        - ``Series`` : 包含单只股票基本信息(当 ``stock_codes`` 是字符串时)
        - ``DataFrane`` : 包含多只股票基本信息(当 ``stock_codes`` 是字符串列表时)

    Raises
    ------
    TypeError
        当 ``stock_codes`` 类型不符合要求时

    Examples
    --------
    >>> import efinance as ef
    >>> # 获取单只股票信息
    >>> ef.stock.get_base_info('600519')
    股票代码                  600519
    股票名称                    贵州茅台
    市盈率(动)                 39.38
    市净率                    12.54
    所处行业                    酿酒行业
    总市值          2198082348462.0
    流通市值         2198082348462.0
    板块编号                  BK0477
    ROE                     8.29
    净利率                  54.1678
    净利润       13954462085.610001
    毛利率                  91.6763
    dtype: object

    >>> # 获取多只股票信息
    >>> ef.stock.get_base_info(['600519','300715'])
        股票代码  股票名称  市盈率(动)    市净率  所处行业           总市值          流通市值    板块编号   ROE      净利率           净利润      毛利率
    0  300715  凯伦股份   42.29   3.12  水泥建材  9.160864e+09  6.397043e+09  BK0424  3.97  12.1659  5.415488e+07  32.8765
    1  600519  贵州茅台   39.38  12.54  酿酒行业  2.198082e+12  2.198082e+12  BK0477  8.29  54.1678  1.395446e+10  91.6763

    """
    return "stock"
