import zipfile


# with zipfile.ZipFile("test.ReaperThemeZip", "w", zipfile.ZIP_DEFLATED) as z:
with zipfile.ZipFile("test.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("a.txt", 'text A, a for apple')
    z.writestr("//b.txt", 'text B, b for bee')
    z.writestr("b.txt", 'text BBBBBB')
    z.writestr("sub\\fuck.txt", 'text FUCK, fuck for fuck')
    z.writestr("sub/fuck.txt", 'text FUCK, fuck for fuck')
