package skins

import (
	"github.com/leobbs/leobbs/pkg/version"
)

func GetLeobbsSkin() map[string]string {
	templateImagePath := "/assets/images/leobbs"
	return map[string]string{
		"BuildTag":          version.BuildTag,
		"BuildNum":          version.BuildNum,
		"adminglow":         "#9898BA",
		"adminnamecolor":    "#990000",
		"amoglow":           "pink",
		"amonamecolor":      "#8b008b",
		"banglow":           "#EE111",
		"catback":           "#73A2DE",
		"catbackpic":        templateImagePath + "/bg.gif",
		"catfontcolor":      "#FFFFFF",
		"catsbackpicinfo":   templateImagePath + "/bg.gif",
		"cmoglow":           "#5577AA",
		"cmonamecolor":      "#F76809",
		"cssmaker":          "雷傲科技",
		"cssname":           "LeoBBS",
		"cssurl":            "http://www.leobbs.org/",
		"font":              "宋体",
		"fontcolormisc":     "#000000",
		"fontcolormisc2":    "#000000",
		"fonthighlight":     "#990000",
		"forumcolorone":     "#F3F6FA",
		"forumcolortwo":     "#FFFFFF",
		"forumfontcolor":    "#000000",
		"lastpostfontcolor": "#000000",
		"lbbody":            "bgcolor=#ffffff alink=#333333 vlink=#333333 link=#333333 topmargin=0 leftmargin=0",
		"memglow":           "#9898BA",
		"menubackground":    "#F3F6FA",
		"menubackpic":       templateImagePath + "/cdbg.gif",
		"menufontcolor":     "#000000",
		"miscbackone":       "#FFFFFF",
		"miscbacktwo":       "#F3F6FA",
		"navbackground":     "#F7F7F7",
		"navborder":         "#E6E6E6",
		"navfontcolor":      "#4D76B3",
		"postcolorone":      "#F3F6FA",
		"postcolortwo":      "#FFFFFF",
		"posternamecolor":   "#000066",
		"posternamefont":    "宋体",
		"postfontcolorone":  "#000000",
		"postfontcolortwo":  "#000000",
		"rzglow":            "#778877",
		"rznamecolor":       "#55AA66",
		"skin":              "leobbs",
		"smoglow":           "#9898BA",
		"smonamecolor":      "#990000",
		"tablebordercolor":  "#4D76B3",
		"tablewidth":        "97%",
		"teamglow":          "#cccccc",
		"teamnamecolor":     "#0000ff",
		"titleborder":       "#4D76B3",
		"titlecolor":        "#73A2DE",
		"titlefontcolor":    "#000000",
	}
}
