import iso639
import logging

# all languages
ALL_LANGUAGES = "ab:ace:af:ak:als:am:an:ang:ar:arc:arz:as:ast:av:ay:az:ba:bar:bcl:be:bg:bh:bi:bjn:bm:bn:bo:bpy:br:bs:bug:bxr:ca:cdo:ce:ceb:ch:chr:chy:ckb:co:cr:crh:cs:csb:cu:cv:cy:da:de:diq:dsb:dv:dz:ee:el:eml:en:eo:es:et:eu:ext:fa:ff:fi:fj:fo:fr:frp:frr:fur:fy:ga:gag:gan:gd:gl:glk:gn:got:gu:gv:ha:hak:haw:he:hi:hif:hr:hsb:ht:hu:hy:ia:id:ie:ig:ik:ilo:io:is:it:iu:ja:jbo:jv:ka:kaa:kab:kbd:kg:ki:kk:kl:km:kn:ko:koi:krc:ks:ku:kv:kw:ky:la:lad:lb:lbe:lez:lg:li:lij:lmo:ln:lo:lt:ltg:lv:mdf:mg:mhr:mi:mk:ml:mn:mo:mr:mrj:ms:mt:mwl:my:myv:mzn:na:nah:nap:nds:ne:new:nl:nn:no:nov:nso:nv:ny:oc:om:or:os:pa:pag:pam:pap:pcd:pdc:pfl:pi:pih:pl:pms:pnb:pnt:ps:pt:qu:rm:rmy:rn:ro:ru:rue:rw:sa:sah:sc:scn:sco:sd:se:sg:sh:si:sk:sl:sm:sn:so:sq:sr:srn:ss:st:stq:su:sv:sw:szl:ta:te:tet:tg:th:ti:tk:tl:tn:to:tpi:tr:ts:tt:tum:tw:ty:udm:ug:uk:ur:uz:ve:vec:vep:vi:vls:vo:wa:war:wo:wuu:xal:xh:xmf:yi:yo:za:zea:zh:zu".split(":")

# major languages
MAJOR_LANGUAGES = "ar:as:az:be:bg:bn:ca:cs:da:de:el:en:es:et:fa:fi:fr:gu:ha:he:hi:hr:hu:id:it:ja:kn:ko:ks:ky:lt:lv:mk:ml:mr:mt:my:ne:nl:no:or:pa:pl:ps:pt:rn:ro:ru:si:sk:sl:so:sq:sr:sv:sw:ta:te:th:tr:uk:ur:uz:vi:zh".split(":")

# construct mapping from old 2-character IDs to new 3-character IDs
MAP_2_TO_3 = {}
for lang in ALL_LANGUAGES:
    record = iso639.find(lang)
    if len(lang) not in [2, 3]:
        logging.warn("Language code %s is not of length 2 or 3", lang)
    elif lang == "mo":
        # special case to map Moldovan to Romanian
        MAP_2_TO_3[lang] = "ron"
    elif lang == "sh":
        # special case to map Serbo-Croatian
        MAP_2_TO_3[lang] = "hbs"
    elif len(lang) == 2 and record:
        # if it's length 2 and we have a better ID for it
        MAP_2_TO_3[lang] = record["iso639_2_b"]
    elif len(lang) == 3:
        # if it's already length 3, leave it alone
        MAP_2_TO_3[lang] = lang
    else:
        # if it couldn't be mapped, raise an error
        raise Error("Couldn't find a good three-character iso639 code for original code '%s'" % (lang))
