import re

def brickbasher(w):
    """Find any variation of the word "brick" in any text provided

    Keyword args:
    w -- raw text of a message to check
    """
    # Extended character classes for substitutions
    b = r"[𝑏𝗯bƄ𝕓𝖇Ь𝓫𝚋Ꮟᖯ𝔟ᑲ𝒃𝘣𝒷𝙗𝐛𝖻B𝕭𝙱𝑩𝚩ꓐΒВ𝜝𝛣𝖡𝝗𐊂𐌁𝗕Ｂ𝓑𝞑𝔅ℬ𝘉𝘽ꞴᏴ𝐁ᗷ𐊡𝐵𝔹ß฿8]"
    r_ = r"[Ꭱ𖼵𝙍ꓣƦ𝐑𝖱ᖇ𐒴𝑅𝗥RᏒ𝕽𝓡𝚁𝈖ℛℜℝ𝑹𝘙𝔯ꮁ𝒓𝘳ⲅᴦꭇꭈ𝓇𝙧𝐫𝗋𝑟𝗿rг𝕣𝖗𝓻𝚛®Я]"
    i = r"[𝓲𝞲ꙇⅈｉ𝔦𝘪ӏ𝙞𝚤𝐢і𝑖˛𝕚𝖎Ꭵ𝚒𑣃iɩɪ𝒊𝛊ⅰı𝒾𝜾⍳𝜄ꭵ𝗂𝝸ℹι𝗶ͺ𝚰𝘭І𝖨𝐥ﺍﺎ𝔩ℐℑ𐊊Ⲓ𐌉ℓ𝜤Ɩ𝞘Ι𝚕𝟏∣اＩ𝗅𝕀1𝙄𝓁𐌠𝐼𞸀𞺀׀𝑰ǀӀᛁ𝟭𝕴Iߊｌ𝛪ⵏ𝝞𝕝𝟣ו𞣇𝙡𝓘𝗜𝟙𝑙ןⅠ𝘐١𝒍𝖑￨🯱𝐈l۱ꓲ𖼨𝙸𝟷𝓵|ⅼ⏽𝗹i1íìîï¡|]"
    c = r"[𝑐𝗰сcｃ𝕔ᴄⲥ𐐽𝖈𝓬𝚌ꮯ𝔠ϲ𝒄𝘤𝒸𝙘𝐜𝖼ⅽℂ𝕮C𝙲𝑪𝒞𝖢𐌂𝗖ꓚᏟ𐔜СＣⲤ𝓒Ⅽℭ𝘊𐐕𝘾🝌𝐂𑣲𑣩Ϲ𐊢𝐶cçćč¢©<]"
    k = r"[𝖐𝓴𝚔𝔨k𝒌𝘬𝓀𝙠𝐤𝗄𝑘𝗸𝕜𝑲𝚱𝒦K𝜥𝛫𝖪𝝟𝗞ⲔᛕꓗΚК𝓚𝞙𝔎𝘒Ꮶ𝙆Ｋ𐔘𝐊𝐾𝕂𝕶𝙺kκкĸ]"

    # Allow non-alphanumeric (and underscores) between characters
    sep = r"[\W_]*"

    # Pattern for flexible "brick"
    brick_pattern = f"{b}{sep}{r_}{sep}{i}{sep}{c}{sep}{k}"
    brick_regex = re.compile(brick_pattern, re.IGNORECASE)

    return (
        bool(brick_regex.search(w)) or  # brick regex
        "🧱" in w or                    # brick emoji
        ":brick:" in w.lower() )        # discord brick emoji