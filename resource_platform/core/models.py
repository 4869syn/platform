from django.db import models


class Banner(models.Model):
    title = models.CharField('标题', max_length=100)
    image = models.ImageField('图片', upload_to='banners/')
    link = models.URLField('链接', blank=True)
    sort_order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title


class KnowledgeDoc(models.Model):
    DOC_TYPE_CHOICES = [('docx', 'Word文档'), ('pdf', 'PDF文档')]
    title = models.CharField('文档名称', max_length=200)
    doc_type = models.CharField('文档类型', max_length=10, choices=DOC_TYPE_CHOICES, default='pdf')
    file = models.FileField('文件', upload_to='knowledge/')
    summary = models.TextField('简介摘要', blank=True)
    category = models.CharField('分类', max_length=50, blank=True)
    views = models.IntegerField('浏览量', default=0)
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        verbose_name = '知识文档'
        verbose_name_plural = '知识文档'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class Script(models.Model):
    name = models.CharField('脚本名称', max_length=100)
    scene = models.CharField('适用场景', max_length=200)
    version = models.CharField('版本号', max_length=20, default='1.0.0')
    file = models.FileField('脚本文件', upload_to='scripts/')
    tutorial = models.TextField('使用教程', blank=True)
    downloads = models.IntegerField('下载次数', default=0)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '脚本'
        verbose_name_plural = '脚本'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class Note(models.Model):
    TAG_CHOICES = [('tech', '技术'), ('office', '办公'), ('tool', '工具'), ('life', '生活'), ('other', '其他')]
    title = models.CharField('标题', max_length=200)
    tag = models.CharField('分类标签', max_length=20, choices=TAG_CHOICES, default='tech')
    content = models.TextField('内容')
    intro = models.TextField('简短导读', blank=True)
    author = models.CharField('作者', max_length=50, default='管理员')
    published_at = models.DateTimeField('发布时间', auto_now_add=True)

    class Meta:
        verbose_name = '笔记'
        verbose_name_plural = '笔记'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Tool(models.Model):
    CATEGORY_CHOICES = [
        ('search', '搜索工具'), ('ai', 'AI工具'), ('dev', '开发工具'),
        ('design', '设计工具'), ('ops', '运维工具'), ('convert', '在线转换'), ('other', '其他'),
    ]
    name = models.CharField('工具名称', max_length=100)
    url = models.URLField('官网地址')
    description = models.CharField('简介', max_length=300, blank=True)
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='other')
    is_hot = models.BooleanField('是否热门', default=False)
    is_new = models.BooleanField('是否新增', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '工具'
        verbose_name_plural = '工具'
        ordering = ['-is_hot', '-created_at']

    def __str__(self):
        return self.name


class Announcement(models.Model):
    TYPE_CHOICES = [('new', '资源上新'), ('script', '脚本更新'), ('note', '优质笔记'), ('tool', '工具更新')]
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    ann_type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='new')
    created_at = models.DateTimeField('发布时间', auto_now_add=True)

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
