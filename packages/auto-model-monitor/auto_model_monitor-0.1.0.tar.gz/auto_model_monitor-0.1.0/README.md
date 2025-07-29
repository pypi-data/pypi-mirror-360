# model_monitor

监视模型训练时生成的权重文件，符合条件时发送QQ邮件通知。

# 使用场景

**当你希望在模型训练过程中，当某个指标（例如验证集上的损失或准确率）低于/高于预设阈值时收到邮件通知。这有助于你及时了解模型的性能表现，以便进行必要的调整。**

# 如何使用
## 安装依赖
```bash
pip install model_monitor
```

## 获取QQ授权码
为了给QQ邮箱发送邮件，你需要使用授权码而不是密码。你可以在QQ邮箱的设置中找到它。

**[https://service.mail.qq.com/detail/0/75](https://service.mail.qq.com/detail/0/75)**

![Alt text](img/1.jpg)

## 示例代码
上述配置后，你就可以使用代码了。

测试代码在[tests/test.py](tests/test.py)

效果如下：

![Alt text](img/2.jpg)


# 开发日志

2025-07-04 更新：
- 最初版本发布。

2025-07-05 更新：
- 代码重构。如果你需要重构前的代码，在[tests/quicktest](tests/quicktest/demo.py)中查看。
- 代码打包，上传PyPI。
