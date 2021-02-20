# coding=utf-8
from flask import Blueprint, render_template, session, request, jsonify, send_file, Response, make_response, \
    send_from_directory
from web import bm

gateway = Blueprint("/gateway", __name__)
# sqlSession = bm.BoxSession


###
#   授权文件上传下载管理
###
@gateway.route("/upload/<key_id>", methods=["POST"])
def file_upload(key_id):
    # key_id = request.form.get("key", "")
    rel = request.form.get("rel", None)
    label = request.form.get("index", None)
    filename = request.form.get("filename", "")
    rel = None if rel == "" else rel
    label = None if label == "" else label
    file = request.files.get("file")
    if not file:
        return jsonify({"status": False, "msg": "文件接受失败，当前接口接受一个文件"})
    if key_id == "" or not bm.key_is_exists(key_id):
        return jsonify({"status": False, "msg": "参数错误"})
    if not bm.box_is_enable(key_id):
        return jsonify({"status": False, "msg": "当前分区已被禁用"})
    if not bm.key_is_writable(key_id):
        return jsonify({"status": False, "msg": "当前密钥已被禁止写入"})
    if label and len(label) > 128:
        return jsonify({"status": False, "msg": "关联index长度必须为[0,128]"})
    if rel:
        if len(rel) >= 32 and len(rel) <= 36:
            if bm.file_is_exists_by_rel_id(key_id, rel_id=rel):
                return jsonify({"status": False, "msg": "当前rel已存在"})
        else:
            return jsonify({"status": False, "msg": "rel长度必须为[32,36]"})
    return jsonify({
        "status": True,
        "msg": "上传成功",
        "data": bm.save_file_by_box_id(key_id, file, rel, label,filename)
    })


@gateway.route("/download/by_id/<key>/<file_id>", methods=["GET"])
def file_download(key, file_id):
    # key_id = request.args.get("key", "")
    # file_id = request.args.get("file_id", "")
    if key == "" or not bm.key_is_exists(key):
        return jsonify({"status": False, "msg": "参数错误"})
    if not bm.box_is_enable(key):
        return jsonify({"status": False, "msg": "当前分区已被禁用"})
    if not bm.key_is_readable(key):
        return jsonify({"status": False, "msg": "当前密钥已被禁止读取"})
    if not bm.file_is_exists_by_file_id(key, file_id):
        return jsonify({"status": False, "msg": "文件不存在"})
    res = bm.get_file_info_by_file_key_id(key, file_id)
    response: Response = send_file(res.get("file_path"), as_attachment=True,attachment_filename=res.get("file_name"))
    return response


@gateway.route("/download/by_rel/<key>/<rel>", methods=["GET"])
def file_by_rel_download(key, rel):
    # key_id = request.args.get("key", "")
    # rel = request.args.get("rel", "")
    print(bm.file_is_exists_by_rel_id(key, rel))
    if key == "" or not bm.key_is_exists(key):
        return jsonify({"status": False, "msg": "参数错误"})
    if not bm.box_is_enable(key):
        return jsonify({"status": False, "msg": "当前分区已被禁用"})
    if not bm.key_is_readable(key):
        return jsonify({"status": False, "msg": "当前密钥已被禁止读取"})
    if not bm.file_is_exists_by_rel_id(key, rel):
        return jsonify({"status": False, "msg": "文件不存在"})
    res = bm.get_file_info_by_rel_key_id(key, rel)
    response: Response = send_file(res.get("file_path"), as_attachment=True,attachment_filename=res.get("file_name"))
    return response


@gateway.route("/list/by_key/<key>", methods=["POST"])
def file_list_by_key(key):
    index = request.form.get("index", "")
    if key == "" or not bm.key_is_exists(key):
        return jsonify({"status": False, "msg": "参数错误"})
    if not bm.box_is_enable(key):
        return jsonify({"status": False, "msg": "当前分区已被禁用"})
    if not bm.key_is_readable(key):
        return jsonify({"status": False, "msg": "当前密钥已被禁止读取"})
    res = bm.get_file_list_by_key_id(key, index)
    return jsonify(res)


@gateway.route("/delete/by_id/<key_id>/<file_id>", methods=["POST"])
def file_del_by_id(key_id,file_id):
    index = request.form.get("index", None)
    if key_id == "" or not bm.key_is_exists(key_id) or file_id == "" or file_id is None:
        return jsonify({"status": False, "msg": "参数错误"})
    if not bm.box_is_enable(key_id):
        return jsonify({"status": False, "msg": "当前分区已被禁用"})
    if not bm.key_is_writable(key_id):
        return jsonify({"status": False, "msg": "当前密钥已被禁止写入"})
    bm.del_file_by_id(key_id, file_id,index)
    return jsonify({
        "status": True,
        "msg": "操作成功",
    })

@gateway.route("/delete/by_rel/<key_id>/<rel>", methods=["POST"])
def file_del_by_rel(key_id,rel):
    index = request.form.get("index", None)
    if key_id == "" or not bm.key_is_exists(key_id) or rel == "" or rel is None:
        return jsonify({"status": False, "msg": "参数错误"})
    if not bm.box_is_enable(key_id):
        return jsonify({"status": False, "msg": "当前分区已被禁用"})
    if not bm.key_is_writable(key_id):
        return jsonify({"status": False, "msg": "当前密钥已被禁止写入"})
    bm.del_file_by_rel(key_id, rel,index)
    return jsonify({
        "status": True,
        "msg": "操作成功",
    })

@gateway.route("/view/<key_id>/<file_id>", methods=["GET"])
def view_file(key_id,file_id):
    if key_id == "" or file_id == "":
        return make_response(render_template("error-404.html"), 404)
    else:
        return render_template("manage/gateway/view.html", info={
            "key_id": key_id,
            "file_id": file_id,
            "file": bm.get_file_info_by_file_key_id(key_id, file_id)
        })


@gateway.route("/view_rel/<key_id>/<rel>", methods=["GET"])
def view_rel_file(key_id,rel):
    if key_id == "" or rel == "":
        return make_response(render_template("error-404.html"), 404)
    else:
        res = bm.get_file_info_by_rel_key_id(key_id, rel)
        return render_template("manage/gateway/view.html", info={
            "key_id": key_id,
            "file_id": res.get("file_id"),
            "file": res
        })


@gateway.route("/ico/<file_type>", methods=["GET"])
def icon(file_type):
    file_type = str(file_type).lower()
    print(file_type)
    if(os.path.exists("./static/layui/assets/ico/"+file_type)):
        return send_from_directory("./static/layui/assets/ico/", file_type)
    else:
        return send_from_directory("./static/layui/assets/ico/", "file.png")