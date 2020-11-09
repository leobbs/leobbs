package main

import (
	"gitee.com/leobbs/leobbs/app/controller"
	"gitee.com/leobbs/leobbs/app/controller/account_controller"
	"gitee.com/leobbs/leobbs/app/controller/admin_controller"
	"gitee.com/leobbs/leobbs/pkg/common"
	"github.com/rs/zerolog/log"
	"gorm.io/gorm"

	//	"github.com/fvbock/endless"
	"github.com/gin-gonic/contrib/sessions"
	"github.com/gin-gonic/gin"

	"gitee.com/cnmade/pongo2gin"
)

var (
	Config    *common.AppConfig
	DB        *gorm.DB
)

func main() {

	Config = common.GetConfig()
	DB = common.GetDB(Config)

	r := gin.Default()


	r.HTMLRender = pongo2gin.New(pongo2gin.RenderOptions{
		TemplateDir: "views",
		ContentType: "text/html; charset=utf-8",
		AlwaysNoCache: true,
	})


	r.Static("/assets", "./vol/assets")
	store := sessions.NewCookieStore([]byte("gssecret"))
	r.Use(sessions.Sessions("mysession", store))
	r.GET("/", controller.IndexAction)

	r.GET("/account/login", account_controller.LoginAction)
	r.GET("/account/register", account_controller.RegisterAction)


	admin := r.Group("/admin")
	{
		admin.GET("/", admin_controller.Index)
		admin.GET("/login", admin_controller.LoginAction)
	}
	log.Info().Msg("Server listen on :8083")
	err := r.Run(":8083")
	if err != nil {
		common.LogError(err)
	}
	//endless.ListenAndServe(":8080", r)
}
