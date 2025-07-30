import unittest
import os
from cgc.tests import ResponsesData, DesiredResponsesData
from cgc.commands.volume.volume_responses import (
    volume_list_response,
    volume_create_response,
    volume_delete_response,
    volume_umount_response,
    volume_mount_response,
)
from cgc.commands.compute.compute_responses import (
    compute_create_filebrowser_response,
    compute_create_response,
    compute_delete_response,
    compute_restart_response,
    compute_list_response,
    template_list_response,
    template_get_start_path_response,
)
from cgc.commands.compute.billing.billing_responses import (
    billing_status_response,
    billing_invoice_response,
    stop_events_resource_response,
    stop_events_volume_response,
)
from cgc.utils.response_utils import (
    tabulate_a_response,
    fill_missing_values_in_a_response,
)
from cgc.commands.compute.compute_utils import get_app_list


class TestVolumeResponses(unittest.TestCase):
    def test_volume_list(self):
        result = volume_list_response(ResponsesData.test_volume_list)
        self.assertEqual(result, DesiredResponsesData.test_volume_list)

    def test_volume_list_empty(self):
        result = volume_list_response(ResponsesData.test_volume_list_empty)
        self.assertEqual(result, DesiredResponsesData.test_volume_list_empty)

    def test_volume_create(self):
        result = volume_create_response(ResponsesData.test_volume_create)
        self.assertEqual(result, DesiredResponsesData.test_volume_create)

    def test_volume_create_exists_error(self):
        # TODO: after creating specific dict for warning/error responses
        pass

    def test_volume_delete(self):
        result = volume_delete_response(ResponsesData.test_volume_delete)
        self.assertEqual(result, DesiredResponsesData.test_volume_delete)

    def test_volume_mount(self):
        result = volume_mount_response(ResponsesData.test_volume_mount)
        self.assertEqual(result, DesiredResponsesData.test_volume_mount)

    def test_volume_unmount(self):
        result = volume_umount_response(ResponsesData.test_volume_unmount)
        self.assertEqual(result, DesiredResponsesData.test_volume_unmount)


class TestComputeResponses(unittest.TestCase):
    def test_compute_get_start_path(self):
        result = template_get_start_path_response(
            ResponsesData.test_compute_get_start_path
        )
        desired_response = DesiredResponsesData.test_compute_get_start_path

        self.assertEqual(result, desired_response)

    def test_compute_template_list(self):
        result = template_list_response(ResponsesData.test_compute_template_list)
        self.assertEqual(result, DesiredResponsesData.test_compute_template_list)

    def test_compute_list(self):
        self.maxDiff = None
        result = compute_list_response(True, ResponsesData.test_compute_list)
        self.assertMultiLineEqual(result, DesiredResponsesData.test_compute_list)

    def test_compute_list_no_labels(self):
        result = compute_list_response(True, ResponsesData.test_compute_list_no_labels)
        self.assertMultiLineEqual(
            result, DesiredResponsesData.test_compute_list_no_labels
        )

    def test_compute_list_empty(self):
        result = compute_list_response(True, ResponsesData.test_compute_list_empty)
        self.assertEqual(result, DesiredResponsesData.test_compute_list_empty)

    def test_compute_create_filebrowser(self):
        result = compute_create_filebrowser_response(
            ResponsesData.test_compute_create_filebrowser
        )
        self.assertMultiLineEqual(
            result, DesiredResponsesData.test_compute_create_filebrowser
        )

    def test_compute_create(self):
        result = compute_create_response(ResponsesData.test_compute_create)
        self.assertMultiLineEqual(result, DesiredResponsesData.test_compute_create)

    def test_compute_create_no_volume_found(self):
        result = compute_create_response(
            ResponsesData.test_compute_create_no_volume_found
        )
        self.assertEqual(
            result, DesiredResponsesData.test_compute_create_no_volume_found
        )

    def test_compute_delete(self):
        result = compute_delete_response(ResponsesData.test_compute_delete)
        self.assertEqual(result, DesiredResponsesData.test_compute_delete)

    def test_compute_restart(self):
        result = compute_restart_response(ResponsesData.test_compute_restart)
        self.assertEqual(result, DesiredResponsesData.test_compute_restart)


class TestBillingResponses(unittest.TestCase):
    def test_billing_status(self):
        result = billing_status_response(ResponsesData.test_billing_status)
        self.assertEqual(result, DesiredResponsesData.test_billing_status)

    def test_billing_invoice(self):
        result = billing_invoice_response(*ResponsesData.test_billing_invoice)
        self.assertEqual(result, DesiredResponsesData.test_billing_invoice)

    def test_billing_invoice_empty(self):
        result = billing_invoice_response(*ResponsesData.test_billing_invoice_empty)
        self.assertEqual(result, DesiredResponsesData.test_billing_invoice_empty)

    def test_billing_stop_events_resource(self):
        result = stop_events_resource_response(
            ResponsesData.test_billing_stop_events_resource
        )
        self.assertEqual(result, DesiredResponsesData.test_billing_stop_events_resource)

    def test_billing_stop_events_volume(self):
        result = stop_events_volume_response(
            ResponsesData.test_billing_stop_events_volume
        )
        self.assertEqual(result, DesiredResponsesData.test_billing_stop_events_volume)

    def test_billing_no_stop_events_volume(self):
        result = stop_events_volume_response(
            ResponsesData.test_billing_no_stop_events_volume
        )
        self.assertEqual(
            result, DesiredResponsesData.test_billing_no_stop_events_volume
        )

    def test_billing_no_stop_events_resource(self):
        result = stop_events_resource_response(
            ResponsesData.test_billing_no_stop_events_resource
        )
        self.assertEqual(
            result, DesiredResponsesData.test_billing_no_stop_events_resource
        )


# WIP
class TestUtils(unittest.TestCase):
    def test_fill_missing_values_in_response(self):
        result = fill_missing_values_in_a_response(
            ResponsesData.test_fill_missing_values_in_response
        )
        self.maxDiff = None
        self.assertListEqual(
            result, DesiredResponsesData.test_fill_missing_values_in_response
        )

    def test_fill_missing_values_in_response_empty(self):
        result = fill_missing_values_in_a_response(
            ResponsesData.test_fill_missing_values_in_response_empty
        )
        self.assertListEqual(
            result, DesiredResponsesData.test_fill_missing_values_in_response_empty
        )

    def test_fill_missing_values_in_response_empty_and_full_in_2_lists(self):
        result = fill_missing_values_in_a_response(
            ResponsesData.test_fill_missing_values_in_response_empty_and_full_in_2_lists
        )
        self.assertListEqual(
            result,
            DesiredResponsesData.test_fill_missing_values_in_response_empty_and_full_in_2_lists,
        )

    def test_tabulate_a_response(self):
        result = tabulate_a_response(ResponsesData.test_tabulate_a_response)
        self.assertEqual(result, DesiredResponsesData.test_tabulate_a_response)

    def test_tabulate_a_response_empty(self):
        result = tabulate_a_response(ResponsesData.test_tabulate_a_response_empty)
        self.assertEqual(result, DesiredResponsesData.test_tabulate_a_response_empty)

    def test_tabulate_a_response_empty_and_full_in_2_lists(self):
        result = tabulate_a_response(
            ResponsesData.test_tabulate_a_response_empty_and_full_in_2_lists
        )
        self.assertEqual(
            result,
            DesiredResponsesData.test_tabulate_a_response_empty_and_full_in_2_lists,
        )

    def test_get_app_list(self):
        self.maxDiff = None
        result = get_app_list(ResponsesData.test_get_app_list, True)
        self.assertListEqual(result, DesiredResponsesData.test_get_app_list)

    def test_get_app_list_not_detailed(self):
        result = get_app_list(ResponsesData.test_get_app_list_not_detailed, False)
        self.assertListEqual(
            result, DesiredResponsesData.test_get_app_list_not_detailed
        )

    def test_get_app_list_missing_labels(self):
        result = get_app_list(ResponsesData.test_get_app_list_missing_labels, True)
        self.maxDiff = None
        self.assertListEqual(
            result, DesiredResponsesData.test_get_app_list_missing_labels
        )

    def test_get_app_list_missing_and_correct_lables_in_2_pods(self):
        result = get_app_list(
            ResponsesData.test_get_app_list_missing_and_correct_lables_in_2_pods, True
        )
        self.assertListEqual(
            result,
            DesiredResponsesData.test_get_app_list_missing_and_correct_lables_in_2_pods,
        )


if __name__ == "__main__":
    unittest.main()
