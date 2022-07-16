def getTranslationFor(phrase="", lang="en"):
    if phrase != "" and lang is not None:
        if phrase == "Movies From The Collection":
            if lang == "ar":
                return "أفلام من السلسلة"
            else:
                return phrase

        elif phrase == "Similar Movies":
            if lang == "ar":
                return "أفلام مشابهة"
            else:
                return phrase

        elif "Popular " in phrase and " Movies" in phrase and " in " not in phrase:
            if lang == "ar":
                return phrase.replace("Popular", "أفلام").replace("Movies", "مشهورة")
            else:
                return phrase

        elif phrase == "Also From ":
            if lang == "ar":
                return "أفلام أخرى من "
            else:
                return phrase

        elif phrase == "People Who Liked This Also Liked":
            if lang == "ar":
                return "الناس اللذين أعجبهم هذا أعجبهم أيضاََ"
            else:
                return phrase

        elif phrase == "Recommended By Hobbitor" or phrase =="Hobbitor Recommendations" or phrase =="Hobbitor Recommendation":
            if lang == "ar":
                return "ترشيحات من المهوياتي"
            else:
                return phrase

        elif phrase == "Spotify Song Recommendations":
            if lang == "ar":
                return "ترشيحات سبوتيفاي"
            else:
                return phrase
        elif phrase == "Quick Picks":
            if lang == "ar":
                return "اختيارات سريعة"
            else:
                return phrase

        elif phrase == "Songs From Your Favourite Artists":
            if lang == "ar":
                return "من المغنيين المفضلين لديك"
            else:
                return phrase

        elif phrase == "Based On The Artists You Like":
            if lang == "ar":
                return "بناءاََ على إختياراتك للمغنيين"
            else:
                return phrase

        elif phrase == "Artists You May Like":
            if lang == "ar":
                return "مغنيين يمكن أن يعجبوك"
            else:
                return phrase

        elif phrase == "Based on Genres You Liked":
            if lang == "ar":
                return "بناءاََ على أنواع الموسيقى اللتي تحبها"
            else:
                return phrase

        elif phrase == "Based on Movies You Liked":
            if lang == "ar":
                return "بناءاََ على الأفلام اللتي أعجبتك"
            else:
                return phrase

        elif phrase == "You May Also Like":
            if lang == "ar":
                return "يمكن أن يعجبك أيضاََ"
            else:
                return phrase

        elif " Top Songs" in phrase:
            if lang == "ar":
                return "أكثر الأغاني شعبية من " + phrase.replace(" Top Songs", "")
            else:
                return phrase

        elif phrase == "Artists Like ":
            if lang == "ar":
                return "مغنيين مثل "
            else:
                return phrase

        elif phrase == "Best Sellers":
                if lang == "ar":
                    return "الأكثر مبيعاََ"
                else:
                    return phrase

        elif "Popular " in phrase and " Books" in phrase:
            if lang == "ar":
                return phrase.replace("Popular", "كتب").replace("Books", "مشهورة")
            else:
                return phrase

        elif " Books" in phrase:
            if lang == "ar":
                return "كتب " + phrase.replace(" Books" , "")
            else:
                return phrase

        elif phrase =="Works By ":
            if lang == "ar":
                return "من أعمال "
            else:
                return phrase

        elif phrase =="Trending Movies Today":
            if lang == "ar":
                return "الأفلام الرائجة اليوم"
            else:
                return phrase

        elif phrase =="Trending Movies This Week":
            if lang == "ar":
                return "الأفلام الرائجة هذا الاسبوع"
            else:
                return phrase

        elif phrase =="Upcoming Movies":
            if lang == "ar":
                return "أفلام ستصدر قريباََ"
            else:
                return phrase

        elif phrase =="Popular Movies in ":
            if lang == "ar":
                return "أفلام مشهورة في عام "
            else:
                return phrase

        elif phrase =="Top Rated Movies":
            if lang == "ar":
                return "الأفلام الأعلى تقييماََ"
            else:
                return phrase

        elif phrase =="People Like You Also Viewed":
            if lang == "ar":
                return "مستخدمين مثلك شاهدو أيضاََ"
            else:
                return phrase

        elif phrase =="New Albums":
            if lang == "ar":
                return "ألبومات جديدة"
            else:
                return phrase