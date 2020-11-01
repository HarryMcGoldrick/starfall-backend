def jwt_required(func):
	@wraps(func)
	def jwt_required_wrapper(*args, **kargs):
		token = request.args.get("token")
		if not token:
			return jsonify({"message": "Token is missing"}, 401)
		try:
			data = jwt.decode(token, app.config["SECRET_KEY"])
		except:
			return jsonify({"message": "Token is invalid"}, 401)
		return func(*args, **kargs)
	return jwt_required_wrapper