## 1. 前端调整

- [x] 1.1 移除用户相关页面（src/views/user/）中的工号字段展示和输入项
	- [x] 1.2 移除用户 API（src/api/user.ts）中工号相关参数
	- [x] 1.3 用户表单手机号注册时可编辑，编辑时禁用（src/views/user/、src/components/user/）
	- [x] 1.4 手机号字段前端校验必填、唯一，注册时校验重复
	- [x] 1.5 登录页面与登录 API 仅支持手机号登录（src/views/login/LoginView.vue、src/api/auth.ts）

## 2. 后端调整

	- [x] 2.1 数据库迁移脚本：移除工号字段，手机号加唯一约束（alembic/versions/）
	- [x] 2.2 models/user.py：去除工号字段，手机号字段加 unique=True
	- [x] 2.3 schemas/user.py：去除工号相关 schema，手机号只允许注册时写入
	- [x] 2.4 routers/users.py：注册时校验手机号唯一，编辑时禁止手机号变更
	- [x] 2.5 登录接口仅支持手机号登录（routers/auth.py、schemas/auth.py）

## 3. 数据清理与测试

	- [x] 3.1 检查并处理现有用户手机号为空或重复的数据（脚本或手动）
	- [x] 3.2 测试注册、编辑、展示等相关功能，确保手机号不可修改、工号已移除
