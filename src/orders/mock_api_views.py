from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class MockCartAPIView(APIView):
    """
    Mock Cart API for testing without authentication
    GET /api/v1/carts/ - Get cart items
    POST /api/v1/carts/ - Add item to cart
    """
    def get(self, request):
        try:
            # Return mock cart data
            mock_cart = {
                "items": [
                    {
                        "id": 1,
                        "amount": 2,
                        "item": {
                            "id": 1,
                            "name": "Test Product 1",
                            "preview": "https://via.placeholder.com/300x200",
                            "amount": {"amount__sum": 100},
                            "subcategory": {
                                "id": 1,
                                "name": "Electronics",
                                "category": {
                                    "id": 1,
                                    "name": "Technology"
                                }
                            },
                            "uom": {
                                "name": "шт"
                            }
                        }
                    }
                ]
            }
            return Response(mock_cart)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Add item to cart
        """
        try:
            data = request.data
            item_id = data.get('item_id')
            amount = data.get('amount', 1)
            
            # Mock response for adding to cart
            response_data = {
                "success": True,
                "message": "Item added to cart",
                "item_id": item_id,
                "amount": amount
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error adding to cart: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
