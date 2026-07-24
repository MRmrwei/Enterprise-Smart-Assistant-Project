package svc

import (
	"ai/service-mcp/internal/config"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"time"
)

type ServiceContext struct {
	Config config.Config
	db     *gorm.DB
}

func (s *ServiceContext) GetConfig() config.Config {
	return s.Config
}

func (s *ServiceContext) DB() *gorm.DB {
	return s.db
}

func NewServiceContext(c config.Config) *ServiceContext {
	return &ServiceContext{
		Config: c,
		db:     db(c),
	}
}

func db(c config.Config) *gorm.DB {

	// 连接数据库
	db, err := gorm.Open(mysql.Open(c.Mysql.DataSource), &gorm.Config{
		// 其他配置
		SkipDefaultTransaction: true, // 跳过默认事务以提高性能
		PrepareStmt:            true, // 预编译 SQL
	})
	if err != nil {
		panic("数据库连接失败:" + err.Error())
	}

	// 获取底层 sql.DB 对象进行连接池配置
	sqlDB, err := db.DB()
	if err != nil {
		panic("数据库连接失败: " + err.Error())
	}

	// 设置连接池
	sqlDB.SetMaxIdleConns(c.Mysql.MaxIdleConns)
	sqlDB.SetMaxOpenConns(c.Mysql.MaxOpenConns)
	sqlDB.SetConnMaxLifetime(time.Hour)

	return db
}
