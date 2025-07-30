from lesscode_utils.es_utils import es_condition_by_terms, es_condition_by_wildcard


def get_single_tag_condition(tag):
    should = []
    if tag == "省级专精特新":
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": ["省级专精特新企业"]}},
                                         {"bool": {
                                             "must_not": [{"terms": {"tags.diy_tag": ["国家级专精特新企业"]}}]}}]}})
    if tag in ["国家级专精特新", "国家级单项冠军", "瞪羚"]:
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": [tag + "企业"]}}]}})
    if tag in ["高新技术企业", "央企", "瞪羚企业", "中国企业500强", "中国民营企业500强", "制造业500强",
               "全球独角兽企业", "中国独角兽企业"]:
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": [tag]}}]}})
    if tag in ["单项冠军"]:
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": ["国家级单项冠军企业"]}}]}})
    if tag in ["单项冠军_ALL"]:
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": ["国家级单项冠军企业", "省级单项冠军企业"]}}]}})
    if tag in ["专精特新"]:
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": ["省级专精特新企业", "国家级专精特新企业"]}}]}})
    if tag in ["中国民营企业500强"]:
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": ["中国民营企业500强"]}}]}})
    if tag in ["A股上市"]:
        should.append(
            {"bool": {"must": [{"terms": {"tags.market_tag.block": ["主板上市", "科创板上市", "创业板上市", "北交所"]}},
                               {"terms": {"tags.market_tag.status": ["已上市"]}}]}})
    if tag in ["新三板"]:
        should.append({"bool": {"must": [{"terms": {"tags.market_tag.status": ["新三板挂牌"]}}]}})
    if tag in ["已上市", "排队上市", "已退市"]:
        should.append({"bool": {"must": [{"terms": {"tags.market_tag.status": [tag]}}]}})
    if tag in ["主板上市", "创业板上市", "科创板上市", "新三板-基础层", "新三板-创新层", "新三板-精选层", "北交所"]:
        should.append({"bool": {"must": [{"terms": {"tags.market_tag.block": [tag]}}]}})
    if tag in ["国有大型企业"]:
        should.append({"bool": {"must": [{"terms": {"tags.capital_type": ["国有"]}},
                                         {"terms": {"tags.scale_tag": ["大型"]}}]}})
    if tag in ["大型企业"]:
        should.append({"bool": {"must": [{"terms": {"tags.scale_tag": ["大型"]}}]}})
    if tag in ["国有企业"]:
        should.append({"bool": {"must": [{"terms": {"tags.capital_type": ["国有"]}}]}})
    if tag in ["省级单项冠军"]:
        should.append({"bool": {"must": [{"terms": {"tags.diy_tag": ["省级单项冠军企业"]}}]}})

    # 其他  -此类不标准，尽量不要使用
    if tag in ["小巨人", "一条龙"]:
        should.append({"bool": {"must": [{"wildcard": {"tags.national_tag.tag_name": f"*{tag}*"}}]}})
    if tag in ["隐形冠军", "成长", "小巨人", "首台套", "雏鹰"]:
        should.append({"bool": {"must": [{"wildcard": {"tags.province_tag.tag_name": f"*{tag}*"}}]}})
    if tag in ["雏鹰"]:
        should.append({"bool": {"must": [{"wildcard": {"tags.city_tag.tag_name": f"*{tag}*"}}]}})
    if tag in ["雏鹰"]:
        should.append({"bool": {"must": [{"wildcard": {"tags.district_tag.tag_name": f"*{tag}*"}}]}})
    if tag in ["独角兽", "世界500强"]:
        should.append({"bool": {"must": [{"wildcard": {"tags.rank_tag.rank_name": f"*{tag}*"}}]}})
    if tag in ["科技型中小企业"]:
        should.append({"bool": {"must": [{"terms": {"tags.certification.certification_name": [tag]}}]}})
    if tag in ["规上企业"]:
        should.append({"bool": {"must": [{"terms": {"tags.nonpublic_tag": [tag]}}]}})
    condition = {"bool": {"should": should}}
    return condition


def format_param_tag(bool_should_more_list, especial_tag_list):
    bool_should_list = []
    if especial_tag_list is not None:
        for tag in especial_tag_list:
            if tag in ["民营", "外资"]:
                bool_should_list.append({"terms": {"tags.capital_type": [tag]}})
            if tag == "省级专精特新":
                bool_should_list.append(
                    {"bool":
                        {"must": [
                            {"terms": {"tags.diy_tag": ["省级专精特新企业"]}},
                            {"bool": {"must_not": [{"terms": {"tags.diy_tag": ["国家级专精特新企业"]}}]}}
                        ]
                        }
                    })
            if tag in ["国家级专精特新", "国家级单项冠军", "瞪羚", "省级单项冠军"]:
                es_condition_by_terms(bool_should_list, "tags.diy_tag", [tag + "企业"])

            if tag in ["高新技术企业", "央企", "瞪羚企业", "中国企业500强", "中国民营企业500强", "制造业500强",
                       "全球独角兽企业", "中国独角兽企业"]:
                es_condition_by_terms(bool_should_list, "tags.diy_tag", [tag])
            if tag in ["单项冠军"]:
                es_condition_by_terms(bool_should_list, "tags.diy_tag", ["国家级单项冠军企业"])
            if tag in ["专精特新"]:
                es_condition_by_terms(bool_should_list, "tags.diy_tag", ["省级专精特新企业", "国家级专精特新企业"])
            # 需评估 "A股上市" 是不是还有存在的额必要  是不是都用 "上市企业"
            if tag in ["A股上市"]:
                bool_should_list.append(
                    {"bool":
                        {"must": [
                            {"terms": {"tags.market_tag.block": ["主板上市", "科创板上市", "创业板上市", "北交所"]}},
                            {"terms": {"tags.market_tag.status": ["已上市"]}}
                        ]
                        }
                    })
            if tag in ["上市企业"]:
                bool_should_list.append(
                    {"bool":
                        {"must": [
                            {"terms": {
                                "tags.market_tag.block": ["主板上市", "创业板上市", "科创板上市", "北交所", "港股主板",
                                                          "港股创业板", "中概股主板", "中概股创业板"]}},
                            {"terms": {"tags.market_tag.status": ["已上市"]}}
                        ]
                        }
                    })
            if tag in ["新三板"]:
                es_condition_by_terms(bool_should_list, "tags.market_tag.status", ["新三板挂牌"])
            if tag in ["已上市", "排队上市", "已退市"]:
                es_condition_by_terms(bool_should_list, "tags.market_tag.status", [tag])
            if tag in ["主板上市", "创业板上市", "科创板上市", "新三板-基础层", "新三板-创新层", "新三板-精选层",
                       "北交所"]:
                es_condition_by_terms(bool_should_list, "tags.market_tag.block", [tag])
            # 其他  -此类不标准，尽量不要使用
            if tag in ["小巨人", "一条龙"]:
                es_condition_by_wildcard(bool_should_list, "tags.national_tag.tag_name", tag)
            if tag in ["隐形冠军", "成长", "小巨人", "首台套", "雏鹰"]:
                es_condition_by_wildcard(bool_should_list, "tags.province_tag.tag_name", tag)
            if tag in ["雏鹰"]:
                es_condition_by_wildcard(bool_should_list, "tags.city_tag.tag_name", tag)
            if tag in ["雏鹰"]:
                es_condition_by_wildcard(bool_should_list, "tags.district_tag.tag_name", tag)
            if tag in ["独角兽", "世界500强"]:
                es_condition_by_wildcard(bool_should_list, "tags.rank_tag.rank_name", tag)
            if tag in ["科技型中小企业"]:
                es_condition_by_terms(bool_should_list, "tags.certification.certification_name", [tag])
            if tag in ["规上企业"]:
                es_condition_by_terms(bool_should_list, "tags.nonpublic_tag", [tag])
    bool_should_more_list.append(bool_should_list)
    return bool_should_more_list


def parse_special_tag_new(tags, tags_param_list=None):
    """新版产业通 特色标签 解析，临时用等数据组将标签添加到diy_tag修改此方法"""
    result = []
    for tag in tags.get("market_tag", []):
        if tag.get("status", "") == "已上市" and tag.get("block", "") in ["主板上市", "科创板上市", "创业板上市",
                                                                          "北交所"]:
            result.append("A股上市")
        if tag.get("status", "") == "新三板挂牌":
            result.append("新三板")
    for tag in tags.get("diy_tag", []):
        for t in ["国家级专精特新", "省级专精特新", "国家级单项冠军", '瞪羚']:
            if t in tag:
                result.append(t)
        if tag in ["央企"]:
            result.append(tag)
    for tag in tags.get("province_tag", []):
        if "单项冠军" in tag.get("tag_name", ""):
            result.append("省级单项冠军")
    for tag in tags.get("rank_tag", []):
        if "独角兽" in tag.get("rank_name", ""):
            result.append("独角兽")
        if "中国企业500强" in tag.get("rank_name", ""):
            result.append("中国企业500强")
    for tag in tags.get("certification", []):
        if tag.get("certification_name", "") in ["科技型中小企业", "高新技术企业"]:
            result.append(tag.get("certification_name", ""))
    if tags_param_list:
        result = list(set(tags_param_list) & set(result))
    else:
        result = list(set(result))
    return result


def format_special_tag_list(special_tag_list=None):
    bool_should_list = []
    if special_tag_list:
        for special_tag in special_tag_list:
            if isinstance(special_tag, list):
                bool_must_list = []
                for _tag in special_tag:
                    bool_must_list.append(get_single_tag_condition(_tag))
                bool_should_list.append({"bool": {"must": bool_must_list}})
            else:
                bool_should_list.append(get_single_tag_condition(special_tag))
    return {"bool": {"should": bool_should_list}}


def format_ck_param_tag(bool_should_more_list, especial_tag_list, bool_relation="or"):
    diy_tag = {
        "员工增长快": 1,
        "新增专利多": 2,
        "高新技术企业": 4,
        "区域拓展快": 5,
        "新获投资多": 6,
        "技术实力": 7,
        "国家级专精特新企业": 8,
        "省级单项冠军企业": 11,
        "国家级单项冠军企业": 13,
        "龙头企业": 9,
        "中国企业500强": 17,
        "中国民营企业500强": 14,
        "中国独角兽企业": 16,
        "全球独角兽企业": 15,
        "央企": 18,
        "股转所需求企业": 19,
        "世界企业500强": 20
    }

    bool_should_list = {"relation": bool_relation, "value": []}
    if especial_tag_list is not None:
        for tag in especial_tag_list:
            if tag in ["已上市", "新三板挂牌"]:
                market_tag = {
                    "已上市": 1,
                    "新三板挂牌": 2
                }
                bool_should_list["value"].append({
                    "relation": "has",
                    "column": "market_tag.status",
                    "value": market_tag[tag]
                })

            if diy_tag.get(tag) is not None:
                bool_should_list["value"].append({
                    "relation": "has",
                    "column": "diy_tag_id",
                    "value": diy_tag[tag]
                })
            if tag == "省级专精特新企业":
                bool_should_list["value"].append({
                    "relation": "and",
                    "value": [{"relation": "has", "column": "diy_tag_id", "value": 3},
                              {"relation": "not",
                               "value": [
                                   {"relation": "has", "column": "diy_tag_id", "value": 8}]}]
                })
            if tag == "科技型中小企业":
                bool_should_list["value"].append({
                    "relation": "has",
                    "column": "certification.name_id",
                    "value": 3
                })
            if tag in ["民营", "外资"]:
                capital_type = {
                    "民营": 2,
                    "外资": 6
                }
                bool_should_list["value"].append({
                    "relation": "eq",
                    "column": "capital_type",
                    "value": capital_type[tag]
                })

    bool_should_more_list.append(bool_should_list)
    return bool_should_more_list
