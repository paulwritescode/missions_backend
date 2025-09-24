from ninja import Router

router = Router(
    tags=["users"],
)


@router.get("/")
def list_users(request):
    return {"message": "List of users"}