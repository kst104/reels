import sys, re
from fontTools.ttLib import TTCollection
from fontTools import subset
html = open(sys.argv[1], encoding="utf-8").read()
# text = everything visible (strip tags/script/style) + digits/punct for counters
body = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S)
text = re.sub(r"<[^>]+>", " ", body)
chars = set(text) | set("0123456789,.·?!%℃①②③ ")
out_dir = sys.argv[2]
for weight, path in (("Regular", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
                     ("Bold", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")):
    col = TTCollection(path)
    font = next(f for f in col.fonts if "CJK KR" in f["name"].getDebugName(1))
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]
    s = subset.Subsetter(opts); s.populate(text="".join(chars)); s.subset(font)
    opts2 = opts
    dst = f"{out_dir}/NotoSansKR-{weight}.woff2"
    subset.save_font(font, dst, opts2)
    print(dst, font["name"].getDebugName(4))
