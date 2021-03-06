package orm_model

import (
	"gorm.io/gorm"
	"time"
)

type Forum struct {
	ID        int64 `gorm:"primarykey"`
	CreatedAt time.Time
	UpdatedAt time.Time
	DeletedAt gorm.DeletedAt `gorm:"index"`
	Name string
	Description string
	Owners string
	ParentForumId int64
	CategoryId int64
	IsDeleted bool
	IsLocked bool
}
