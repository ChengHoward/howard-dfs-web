import json, os, configparser, psutil, uuid

from flask import Blueprint, render_template, session, request, jsonify, make_response, send_from_directory, send_file

from empty.BoxEmpty import Box, BoxKey
from web import user_page, user_data, dir_is_not_null, bm

file_box = Blueprint("/file_box", __name__)


###
#   文件分区管理接口
###
@file_box.route("/", methods=["GET"])
@user_page
def boxs():
    return render_template("manage/file_box/boxs.html")


@file_box.route("/boxs.json", methods=["GET", "POST"])
@user_page
def boxs_data():
    boxSession = bm.getBoxSession()
    res_json = {
        "msg": "",
        "count": boxSession.query(Box).filter_by(v_del=False).count(),
        "code": 0,
        "status": True,
        "data": bm.get_box_info_by_all()
    }
    boxSession.close()
    return jsonify(res_json)

def getInitPath(path, next_path="", dir_list=None):
    _path = os.path.dirname(path)
    if (dir_list is None):
        next_path = path
        path = _path
        _path = os.path.dirname(path)
    if (next_path == path):
        return [{"name": _.device, "value": _.device, "children": dir_list if path == _.device else [],
                 "selected": dir_list is None and next_path == _.device}
                for _ in psutil.disk_partitions()]
    else:
        return getInitPath(_path, path, [{"name": _, "value": os.path.join(path, _),
                                          "children": dir_list if next_path == os.path.join(path, _) else [],
                                          "selected": dir_list is None and next_path == os.path.join(path, _)}
                                         for _ in os.listdir(path) if os.path.isdir(os.path.join(path, _))])


@file_box.route("/disk.json", methods=["GET", "POST"])
@user_page
def disk_info():
    if request.method == "GET":
        data = request.args
    else:
        data = request.form
    path = data.get("box_path", None)
    init = True if data.get("init", False) else False
    if not path:
        return jsonify({
            "status": True,
            "data": [{"name": _.device, "value": _.device, "children": []}
                     for _ in psutil.disk_partitions()]
        })
    else:
        if init:
            return jsonify({
                "status": True,
                "data": getInitPath(path)
            })
        else:
            if os.path.exists(path):
                print([_ for _ in os.listdir(path) if os.path.isdir(os.path.join(path, _))])
                return jsonify({
                    "status": True,
                    "data": [
                        {"name": _, "value": os.path.join(path, _),
                         "children": [] }
                        for _ in os.listdir(path) if os.path.isdir(os.path.join(path, _))]
                })
            else:
                return jsonify({
                    "status": False,
                    "msg": "路径不存在"
                })


@file_box.route("/addBox.json", methods=["POST"])
@user_page
def add_box():
    data = request.form
    box_path = data.get("box_path", "")
    box_name = data.get("box_name", "")
    mark = data.get("mark", "")
    enable = True if data.get("enable", False) else False
    if box_path == "" or box_name == "":
        return jsonify({"status": False, "msg": "参数错误"})
    sqlSession = bm.getBoxSession()
    sqlSession.add(Box(box_id=str(uuid.uuid4()),
                       box_path=box_path,
                       box_name=box_name,
                       box_mark=mark,
                       enable=enable,
                       v_del=False))
    sqlSession.commit()
    sqlSession.commit()
    sqlSession.close()
    return jsonify({"status": True, "msg": "创建成功"})


@file_box.route("/delBox.json", methods=["POST"])
@user_page
def del_box():
    data = request.form
    box_id = data.get("box_id", "")
    if box_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    # sqlSession.query(Box).filter(Box.box_id == box_id).delete()
    # sqlSession.commit()
    sqlSession = bm.getBoxSession()
    sqlSession.query(Box).filter_by(box_id=box_id).update({"v_del": True})
    sqlSession.commit()
    sqlSession.close()
    return jsonify({"status": True, "msg": "删除成功"})


@file_box.route("/editBox.json", methods=["POST"])
@user_page
def edit_box():
    data = request.form
    box_id = data.get("box_id", "")
    box_path = data.get("box_path", "")
    box_name = data.get("box_name", "")
    mark = data.get("mark", "")
    enable = True if data.get("enable", False) else False
    if box_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    sqlSession = bm.getBoxSession()
    sqlSession.query(Box).filter_by(box_id=box_id).update({
        'box_name': box_name,
        # 'box_path': box_path,
        'box_mark': mark,
        'enable': enable,
    })
    # bm.enable_update(box_id,enable)
    sqlSession.commit()
    sqlSession.close()
    return jsonify({"status": True, "msg": "修改成功"})


@file_box.route("/enable.json", methods=["POST"])
@user_page
def enable_edit():
    data = request.form
    box_id = data.get("box_id", "")
    enable = True if data.get("enable", False) else False
    if box_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    sqlSession = bm.getBoxSession()
    sqlSession.query(Box).filter_by(box_id=box_id).update({'enable': enable, })
    sqlSession.commit()
    sqlSession.close()
    # bm.enable_update(box_id,enable)
    return jsonify({"status": True, "msg": "修改成功"})


###
#   Key管理接口
###
# @file_box.route("/Keylist.json", methods=["POST"])
# @user_page
# def enable_edit():
#     data = request.form
#     sqlSession = SqlSession()
#     print(data.get("enable", ""))
#     box_id = data.get("box_id", "")
#     enable = True if data.get("enable", False) else False
#     if box_id == "":
#         return jsonify({"status": False, "msg": "参数错误"})
#     sqlSession.query(Box).filter_by(box_id=box_id).update({'enable': enable,})
#     sqlSession.commit()
#     return jsonify({"status": True, "msg": "修改成功"})

@file_box.route("/gen.page", methods=["GET"])
@user_page
def gen_page():
    key_id = request.args.get("key_id", "")
    box: Box = bm.get_box_by_key_id(key_id)

    if not key_id == "":
        return render_template("manage/file_box/gen.html",
                               info={
                                   "host_url": request.host_url
                               },
                               box_id=box.box_id, key_id=key_id)
    else:
        return make_response(render_template("error-404.html"), 404)


###
#   文件密钥管理接口
###
@file_box.route("/keys.page", methods=["GET"])
@user_page
def keys_page():
    box_id = request.args.get("box_id", "")
    if not box_id == "":
        return render_template("manage/file_box/keys.html", box_id=box_id)
    else:
        return make_response(render_template("error-404.html"), 404)


@file_box.route("/keys.json", methods=["GET"])
@user_page
def keys_data():
    box_id = request.args.get("box_id", "")
    if box_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    else:
        res_json = {
            "msg": "",
            "count": bm.get_keys_count_by_box_id(box_id),
            "code": 0,
            "status": True,
            "data": bm.get_keys_by_box_id(box_id)
        }
    return jsonify(res_json)


@file_box.route("/genkey.json", methods=["POST"])
@user_page
def genkey():
    box_id = request.form.get("box_id", "")
    if box_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    sqlSession = bm.getBoxSession()
    sqlSession.add(BoxKey(key_id=str(uuid.uuid4()),
                          box_id=box_id,
                          read_perm=True,
                          write_perm=True,
                          ))
    sqlSession.commit()
    sqlSession.close()
    return jsonify({"status": True, "msg": "生成成功"})


@file_box.route("/delkey.json", methods=["POST"])
@user_page
def del_key():
    data = request.form
    key_id = data.get("key_id", "")
    if key_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    sqlSession = bm.getBoxSession()
    sqlSession.query(BoxKey).filter_by(key_id=key_id).delete()
    sqlSession.commit()
    sqlSession.close()
    return jsonify({"status": True, "msg": "删除成功"})


@file_box.route("/enable_key.json", methods=["POST"])
@user_page
def enable_key():
    data = request.form
    key_id = data.get("key_id", "")
    mode = data.get("mode", "")
    enable = True if data.get("enable", False) else False
    if key_id == "" or not mode in ['read_perm', 'write_perm']:
        return jsonify({"status": False, "msg": "参数错误"})
    # mode = 'read_perm' if mode == 'r' else 'write_perm'
    sqlSession = bm.getBoxSession()
    sqlSession.query(BoxKey).filter_by(key_id=key_id).update({mode: enable, })
    sqlSession.commit()
    sqlSession.close()
    return jsonify({"status": True, "msg": "操作成功"})


###
#   文件分区查看接口
###
@file_box.route("/content.page", methods=["GET"])
@user_page
def box_content():
    # bm.get_path(request.args.get("box_id",""))
    box_id = request.args.get("box_id", "")
    if not box_id == "":
        return render_template("manage/file_box/content.html", box_id=box_id)
    else:
        return make_response(render_template("error-404.html"), 404)


@file_box.route("/ls/<box_id>.json", methods=["POST"])
@user_page
def ls_json(box_id):
    # bm.get_path(request.args.get("box_id",""))
    limit = int(request.form.get("limit", 10))
    page = int(request.form.get("page", 1))
    path = request.form.get("path", "")
    if box_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    else:
        data = bm.get_metadata_dir_list_By_box_id(box_id, path,page,limit)
        return jsonify({
            "code": 0,
            "msg": "",
            "count": bm.get_metadata_dir_count_By_box_id(box_id, path),
            "data": data
        })


@file_box.route("/file/<box_id>/<file_id>", methods=["GET"])
@user_page
def file_download(box_id, file_id):
    if box_id == "" or file_id == "":
        return jsonify({"status": False, "msg": "参数错误"})
    else:
        res = bm.get_file_info_by_file_box_id(box_id, file_id)
        return send_file(res.get("file_path"), as_attachment=True)


@file_box.route("/ico/<file_type>", methods=["GET"])
def icon(file_type):
    file_type = str(file_type).lower()
    print(file_type)
    if(os.path.exists("./static/layui/assets/ico/"+file_type)):
        return send_from_directory("./static/layui/assets/ico/", file_type)
    else:
        return send_from_directory("./static/layui/assets/ico/", "file.png")


@file_box.route("/view.page", methods=["GET"])
@user_page
def view_file():
    box_id = request.args.get("box_id", "")
    file_id = request.args.get("file_id", "")
    if box_id == "" or file_id == "":
        return make_response(render_template("error-404.html"), 404)
    else:
        return render_template("manage/file_box/view.html", info={
            "box_id": box_id,
            "file_id": file_id,
            "file": bm.get_file_info_by_file_box_id(box_id, file_id)
        })
