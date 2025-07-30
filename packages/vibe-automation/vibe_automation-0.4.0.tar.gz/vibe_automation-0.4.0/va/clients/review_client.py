import logging
import va.protos.orby.va.public.execution_service_pb2_grpc as execution_service_grpc
import va.protos.orby.va.public.execution_messages_pb2 as execution_messages

from va.store.execution.execution_client import get_execution_client

logger = logging.getLogger(__name__)


def request_review(execution_id: str):
    execution_client = get_execution_client()
    execution_stub = execution_service_grpc.ExecutionServiceStub(
        execution_client._grpc_channel
    )
    request = execution_messages.RequestReviewRequest(execution_id=execution_id)
    response = execution_client.call_grpc_channel(execution_stub.RequestReview, request)
    return response.review_id


def get_review_status(review_id: str):
    try:
        execution_client = get_execution_client()
        execution_stub = execution_service_grpc.ExecutionServiceStub(
            execution_client._grpc_channel
        )
        request = execution_messages.GetReviewStatusRequest(review_id=review_id)
        response = execution_client.call_grpc_channel(
            execution_stub.GetReviewStatus, request
        )
        return response.status
    except Exception as e:
        logger.error(f"Failed to fetch review status: {e}")
        return None
