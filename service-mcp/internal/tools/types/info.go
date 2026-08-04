package types

type EmployeeInfoResponse struct {
	Uid       int64    `json:"uid" jsonschema_description:"用户id"`
	Name      string   `json:"name" jsonschema_description:"用户名称"`
	RoleNames []string `json:"role_names" jsonschema_description:"用户角色名称,用户拥有多个角色"`
	RoleCodes []string `json:"role_codes" jsonschema_description:"用户角色编码"`
}
