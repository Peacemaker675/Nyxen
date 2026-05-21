from django.db import OperationalError, connections
from django.http import JsonResponse
# Create your views here.

def health_check(request):
	status = {
		"status" : "healthy",
		"services": {
			"database" : "healthy",
		}
	}
	try:
		db_conn = connections["default"]
		db_conn.cursor()
	except OperationalError:
		status["status"] = "unhealthy"
		status["services"]["database"] = "unhealthy"
		return JsonResponse(status, status=503)
	return JsonResponse(status, status=200)
