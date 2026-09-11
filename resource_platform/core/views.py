from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils.html import escape
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import Banner, KnowledgeDoc, Script, Note, Tool, Announcement
import os
import io


def superuser_required(view_func):
    """仅允许超级用户访问的视图装饰器"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden('需要管理员权限才能执行此操作。')
        return view_func(request, *args, **kwargs)
    return wrapper


def _extract_docx_text(file_path):
    """Extract text from DOCX using built-in zipfile + xml (no external deps)."""
    import zipfile
    import xml.etree.ElementTree as ET

    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    html_parts = []

    try:
        with zipfile.ZipFile(file_path, 'r') as z:
            with z.open('word/document.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()

            body = root.find('w:body', ns)
            if body is None:
                return '<p style="color:#999;">无法解析文档结构。</p>'

            for elem in body:
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

                if tag == 'p':
                    # Extract paragraph text
                    texts = []
                    for t in elem.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                        if t.text:
                            texts.append(t.text)
                    para_text = ''.join(texts).strip()
                    if not para_text:
                        continue

                    # Check paragraph style for headings
                    pPr = elem.find('w:pPr', ns)
                    style_name = ''
                    if pPr is not None:
                        pStyle = pPr.find('w:pStyle', ns)
                        if pStyle is not None:
                            style_name = pStyle.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')

                    if 'Heading1' in style_name or style_name == '1':
                        html_parts.append('<h1>' + escape(para_text) + '</h1>')
                    elif 'Heading2' in style_name or style_name == '2':
                        html_parts.append('<h2>' + escape(para_text) + '</h2>')
                    elif 'Heading3' in style_name or style_name == '3':
                        html_parts.append('<h3>' + escape(para_text) + '</h3>')
                    elif 'Heading4' in style_name or style_name == '4':
                        html_parts.append('<h4>' + escape(para_text) + '</h4>')
                    else:
                        html_parts.append('<p>' + escape(para_text) + '</p>')

                elif tag == 'tbl':
                    # Extract table
                    html_parts.append('<table style="width:100%; border-collapse:collapse; margin:16px 0; font-size:14px;">')
                    for tr in elem.findall('w:tr', ns):
                        html_parts.append('<tr>')
                        for tc in tr.findall('w:tc', ns):
                            cell_texts = []
                            for t in tc.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                                if t.text:
                                    cell_texts.append(t.text)
                            cell_text = ''.join(cell_texts).strip()
                            html_parts.append('<td style="border:1px solid #e0e0e0; padding:8px 12px;">' + escape(cell_text) + '</td>')
                        html_parts.append('</tr>')
                    html_parts.append('</table>')

        if not html_parts:
            return '<p style="color:#999;">文档内容为空或无法解析，请下载后查看。</p>'
        return '\n'.join(html_parts)

    except Exception as e:
        return '<p style="color:#999;">无法解析文档内容（' + escape(str(e)) + '），请下载后查看。</p>'


def _extract_pdf_text(file_path):
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(file_path)
        text_parts = []
        for page in reader.pages[:50]:
            text = page.extract_text()
            if text:
                text_parts.append(f'<p>{escape(text)}</p>')
        if text_parts:
            return chr(10).join(text_parts)
    except Exception:
        pass
    return None


@login_required
def index(request):
    banners = Banner.objects.filter(is_active=True)
    announcements = Announcement.objects.all()[:8]
    latest_docs = KnowledgeDoc.objects.all()[:4]
    latest_scripts = Script.objects.all()[:4]
    latest_notes = Note.objects.all()[:4]
    hot_tools = Tool.objects.filter(is_hot=True)[:6]
    new_tools = Tool.objects.filter(is_new=True)[:6]

    context = {
        'banners': banners,
        'announcements': announcements,
        'latest_docs': latest_docs,
        'latest_scripts': latest_scripts,
        'latest_notes': latest_notes,
        'hot_tools': hot_tools,
        'new_tools': new_tools,
        'active_page': 'home',
    }
    return render(request, 'index.html', context)


@login_required
def knowledge_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    docs = KnowledgeDoc.objects.all()

    if query:
        docs = docs.filter(title__icontains=query)
    if category:
        docs = docs.filter(category=category)

    paginator = Paginator(docs, 12)
    page = request.GET.get('page', 1)
    docs_page = paginator.get_page(page)
    categories = KnowledgeDoc.objects.values_list('category', flat=True).distinct()

    context = {
        'docs': docs_page,
        'categories': categories,
        'query': query,
        'current_category': category,
        'active_page': 'knowledge',
    }
    return render(request, 'knowledge.html', context)


@login_required
def doc_detail(request, pk):
    doc = get_object_or_404(KnowledgeDoc, pk=pk)
    doc.views += 1
    doc.save()

    preview_html = ''
    if doc.file:
        file_path = doc.file.path
        if doc.doc_type == 'docx':
            preview_html = _extract_docx_text(file_path)
        elif doc.doc_type == 'pdf':
            preview_html = _extract_pdf_text(file_path)

    context = {
        'doc': doc,
        'preview_html': preview_html,
        'active_page': 'knowledge',
    }
    return render(request, 'doc_detail.html', context)


@superuser_required
def doc_download(request, pk):
    doc = get_object_or_404(KnowledgeDoc, pk=pk)
    if doc.file:
        return FileResponse(doc.file.open('rb'), as_attachment=True, filename=os.path.basename(doc.file.name))
    raise Http404


@login_required
def script_list(request):
    scripts = Script.objects.all()
    context = {'scripts': scripts, 'active_page': 'scripts'}
    return render(request, 'scripts.html', context)


@login_required
def script_detail(request, pk):
    script = get_object_or_404(Script, pk=pk)
    context = {'script': script, 'active_page': 'scripts'}
    return render(request, 'script_detail.html', context)


@superuser_required
def script_download(request, pk):
    script = get_object_or_404(Script, pk=pk)
    script.downloads += 1
    script.save()

    if script.file:
        return FileResponse(script.file.open('rb'), as_attachment=True, filename=os.path.basename(script.file.name))
    raise Http404


@login_required
def note_list(request):
    tag = request.GET.get('tag', '')
    notes = Note.objects.all()

    if tag:
        notes = notes.filter(tag=tag)

    paginator = Paginator(notes, 10)
    page = request.GET.get('page', 1)
    notes_page = paginator.get_page(page)

    context = {
        'notes': notes_page,
        'current_tag': tag,
        'active_page': 'notes'
    }
    return render(request, 'notes.html', context)


@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    context = {'note': note, 'active_page': 'notes'}
    return render(request, 'note_detail.html', context)


@login_required
def tool_list(request):
    category = request.GET.get('category', '')
    tools = Tool.objects.all()

    if category:
        tools = tools.filter(category=category)

    hot_tools = Tool.objects.filter(is_hot=True)
    new_tools = Tool.objects.filter(is_new=True)

    context = {
        'tools': tools,
        'hot_tools': hot_tools,
        'new_tools': new_tools,
        'current_category': category,
        'active_page': 'tools',
    }
    return render(request, 'tools.html', context)


# ==================== 知识文库：上传 / 在线编辑 ====================

def _get_doc_type(filename):
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    if ext == 'docx':
        return 'docx'
    if ext == 'pdf':
        return 'pdf'
    return None


@superuser_required
def doc_upload(request):
    """上传新文档"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', '').strip()
        summary = request.POST.get('summary', '').strip()
        upload_file = request.FILES.get('file')

        if not title or not upload_file:
            messages.error(request, '文档标题和文件不能为空。')
        else:
            doc_type = _get_doc_type(upload_file.name)
            if not doc_type:
                messages.error(request, '仅支持上传 .docx 或 .pdf 格式的文档。')
            else:
                doc = KnowledgeDoc.objects.create(
                    title=title,
                    doc_type=doc_type,
                    file=upload_file,
                    summary=summary,
                    category=category,
                )
                messages.success(request, '文档上传成功！')
                return redirect('core:doc_detail', pk=doc.pk)

    return render(request, 'doc_form.html', {
        'active_page': 'knowledge',
        'is_edit': False,
    })


@superuser_required
def doc_edit(request, pk):
    """在线编辑文档信息（含替换文件）"""
    doc = get_object_or_404(KnowledgeDoc, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', '').strip()
        summary = request.POST.get('summary', '').strip()
        upload_file = request.FILES.get('file')

        if not title:
            messages.error(request, '文档标题不能为空。')
        else:
            doc.title = title
            doc.category = category
            doc.summary = summary
            if upload_file:
                doc_type = _get_doc_type(upload_file.name)
                if not doc_type:
                    messages.error(request, '仅支持上传 .docx 或 .pdf 格式的文档。')
                    return render(request, 'doc_form.html', {
                        'doc': doc, 'active_page': 'knowledge', 'is_edit': True,
                    })
                # 删除旧文件
                if doc.file:
                    doc.file.delete(save=False)
                doc.file = upload_file
                doc.doc_type = doc_type
            doc.save()
            messages.success(request, '文档信息已更新！')
            return redirect('core:doc_detail', pk=doc.pk)

    return render(request, 'doc_form.html', {
        'doc': doc,
        'active_page': 'knowledge',
        'is_edit': True,
    })


@superuser_required
def doc_delete(request, pk):
    """删除文档"""
    doc = get_object_or_404(KnowledgeDoc, pk=pk)
    if request.method == 'POST':
        if doc.file:
            doc.file.delete(save=False)
        doc.delete()
        messages.success(request, '文档已删除。')
    return redirect('core:knowledge')


# ==================== 脚本仓库：上传 / 编辑 ====================

@superuser_required
def script_upload(request):
    """上传新脚本"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        scene = request.POST.get('scene', '').strip()
        version = request.POST.get('version', '').strip() or '1.0.0'
        tutorial = request.POST.get('tutorial', '').strip()
        upload_file = request.FILES.get('file')

        if not name or not upload_file:
            messages.error(request, '脚本名称和文件不能为空。')
        else:
            script = Script.objects.create(
                name=name,
                scene=scene,
                version=version,
                tutorial=tutorial,
                file=upload_file,
            )
            messages.success(request, '脚本上传成功！')
            return redirect('core:script_detail', pk=script.pk)

    return render(request, 'script_form.html', {
        'active_page': 'scripts',
        'is_edit': False,
    })


@superuser_required
def script_edit(request, pk):
    """在线编辑脚本信息（含替换文件）"""
    script = get_object_or_404(Script, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        scene = request.POST.get('scene', '').strip()
        version = request.POST.get('version', '').strip() or '1.0.0'
        tutorial = request.POST.get('tutorial', '').strip()
        upload_file = request.FILES.get('file')

        if not name:
            messages.error(request, '脚本名称不能为空。')
        else:
            script.name = name
            script.scene = scene
            script.version = version
            script.tutorial = tutorial
            if upload_file:
                if script.file:
                    script.file.delete(save=False)
                script.file = upload_file
            script.save()
            messages.success(request, '脚本信息已更新！')
            return redirect('core:script_detail', pk=script.pk)

    return render(request, 'script_form.html', {
        'script': script,
        'active_page': 'scripts',
        'is_edit': True,
    })


@superuser_required
def script_delete(request, pk):
    """删除脚本"""
    script = get_object_or_404(Script, pk=pk)
    if request.method == 'POST':
        if script.file:
            script.file.delete(save=False)
        script.delete()
        messages.success(request, '脚本已删除。')
    return redirect('core:scripts')


# ==================== 笔记分享：新建 / 在线编辑 ====================

@superuser_required
def note_create(request):
    """在线新建笔记"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        tag = request.POST.get('tag', 'tech')
        intro = request.POST.get('intro', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            messages.error(request, '笔记标题和内容不能为空。')
        else:
            note = Note.objects.create(
                title=title,
                tag=tag if tag in dict(Note.TAG_CHOICES) else 'tech',
                intro=intro,
                content=content,
                author=request.user.username,
            )
            messages.success(request, '笔记发布成功！')
            return redirect('core:note_detail', pk=note.pk)

    return render(request, 'note_form.html', {
        'active_page': 'notes',
        'is_edit': False,
    })


@superuser_required
def note_edit(request, pk):
    """在线编辑笔记"""
    note = get_object_or_404(Note, pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        tag = request.POST.get('tag', 'tech')
        intro = request.POST.get('intro', '').strip()
        content = request.POST.get('content', '').strip()

        if not title or not content:
            messages.error(request, '笔记标题和内容不能为空。')
        else:
            note.title = title
            note.tag = tag if tag in dict(Note.TAG_CHOICES) else note.tag
            note.intro = intro
            note.content = content
            note.save()
            messages.success(request, '笔记已更新！')
            return redirect('core:note_detail', pk=note.pk)

    return render(request, 'note_form.html', {
        'note': note,
        'active_page': 'notes',
        'is_edit': True,
    })


@superuser_required
def note_delete(request, pk):
    """删除笔记"""
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, '笔记已删除。')
    return redirect('core:notes')
