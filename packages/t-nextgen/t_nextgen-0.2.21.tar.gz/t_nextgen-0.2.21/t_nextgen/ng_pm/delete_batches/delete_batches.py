"""This module provides a function to delete batches from the database."""
from t_nextgen.config import Config
from t_nextgen.ng_pm.core import NextGenPMCore
from t_nextgen.ng_pm.delete_batches.core import BatchDeleterCore
from t_nextgen.utils.logger import logger


class BatchDeleter(BatchDeleterCore):
    """Class to delete batches from the NextGen PM application."""

    def __init__(
        self,
        next_gen: NextGenPMCore,
        descriptions: list[str],
        practice: str,
    ):
        """Initialize the BatchDeleter object.

        Args:
            next_gen (NextGenPMCore): NextGen PM Core object.
            descriptions (list[str]): List of descriptions of the batches to delete.
            practice (str): Practice name.
        """
        self.next_gen = next_gen
        self.descriptions = descriptions
        self.practice = practice
        self.batches_not_secured_to_thoughtful: list[str] = []
        self.number_of_remits = 0
        self.found_batch_to_delete = False
        self.batches_marked_to_deletion: list[str] = []
        self.batches_not_found_for_deletion: list[str] = []
        self.total_number_of_batches_in_the_practice = 0
        self.batches_not_deleted: list[str] = []
        self.all_batches_secured_to_thoughtful_were_deleted: bool = False

    def check_if_some_batch_was_not_found_for_deletion(self):
        """Check if some batches were not found for deletion."""
        self.batches_not_found_for_deletion = [
            batch
            for batch in self.descriptions
            if (batch not in self.batches_not_secured_to_thoughtful and batch not in self.batches_marked_to_deletion)
        ]
        if self.batches_not_found_for_deletion:
            logger.info(
                f"Some batches were not found for deletion in {self.practice}."
                f"Batches not found: {self.batches_not_found_for_deletion}"
            )

    def check_if_all_batches_were_deleted(self):
        """Check if all batches were deleted."""
        data_items = self.get_batch_rows()
        if self.batches_marked_to_deletion and (
            self.total_number_of_batches_in_the_practice - len(self.batches_not_secured_to_thoughtful)
            == len(data_items)
        ):
            logger.info(f"All batches secured to thoughtful were deleted in {self.practice}")
            self.all_batches_secured_to_thoughtful_were_deleted = True
        else:
            batches_secured_to_thoughtful = [
                batch for batch in self.descriptions if batch not in self.batches_not_secured_to_thoughtful
            ]

            for index, data_item in enumerate(data_items):
                next_gen_description = data_item.descendants(title="Description", control_type="Edit")[0].get_value()
                for description in batches_secured_to_thoughtful:
                    if description in next_gen_description:
                        self.batches_not_deleted.append(description)
                        break
            if self.batches_not_deleted:
                logger.warning(
                    f"Some batches were not deleted in {self.practice}. Batches not deleted: {self.batches_not_deleted}"
                )
                self.all_batches_secured_to_thoughtful_were_deleted = False

    def generate_report(self):
        """Generate a report of the batches that were not deleted."""
        return {
            "practice": self.practice,
            "batches_not_secured_to_thoughtful": self.batches_not_secured_to_thoughtful,
            "number_of_batches_marked_to_deletion": len(self.batches_marked_to_deletion),
            "batches_not_found_for_deletion": self.batches_not_found_for_deletion,
            "batches_not_deleted": self.batches_not_deleted,
            "number_of_batches_to_delete": len(self.descriptions),
            "number_of_batches_not_found_for_deletion": len(self.batches_not_found_for_deletion),
            "number_of_batches_secured_to_thoughtful": len(self.batches_marked_to_deletion),
            "number_of_batches_not_secured_to_thoughtful": len(self.batches_not_secured_to_thoughtful),
            "number_of_batches_in_the_practice": self.total_number_of_batches_in_the_practice,
            "number_of_remits_deleted": self.number_of_remits,
            "all_batches_secured_to_thoughtful_deleted": self.all_batches_secured_to_thoughtful_were_deleted,
        }

    def delete(self) -> dict:
        """Delete the batches."""
        self.next_gen.batch_posting_window.click_batch_icon_from_bar(self.practice)
        data_items = self.get_batch_rows()
        self.total_number_of_batches_in_the_practice = len(data_items)
        for index, data_item in enumerate(data_items):
            next_gen_description = data_item.descendants(title="Description", control_type="Edit")[0].get_value()
            secured_to = data_item.descendants(title="Secured To", control_type="Edit")[0].get_value()
            for description in self.descriptions:
                if description in next_gen_description:
                    if not data_item.is_visible():
                        self.next_gen.desktop_app.click_down_n_times(index)

                    if "thoughtful" in secured_to.lower():
                        members = data_item.descendants(title="Members", control_type="Edit")[0].get_value()
                        self.number_of_remits += int(members)
                        self.found_batch_to_delete = True
                        self.mark_batch_for_deletion(data_item, description)
                        self.batches_marked_to_deletion.append(description)
                    else:
                        self.batches_not_secured_to_thoughtful.append(description)
                        logger.warning(f"Batch {description} is secured to {secured_to}. Not marking it to delete")
                    break
        if self.found_batch_to_delete:
            self.check_if_all_batches_were_selected_correctly()
            logger.info(f"Deleting {self.number_of_remits} remits from {self.practice}")
            self.click_delete_option()
            self.wait_for_deletion_process_to_finish(timeout=self.number_of_remits * 40, interval=40)
        else:
            logger.info(f"No batches found to delete in {self.practice}")
        self.check_if_all_batches_were_deleted()
        self.check_if_some_batch_was_not_found_for_deletion()
        return self.generate_report()


def delete_batches(
    next_gen: NextGenPMCore, batches_to_delete: list[dict], database: str = Config.DATABASES.TEST
) -> list[dict]:
    """Deletes batches from the NextGen PM application.

    Args:
        next_gen (NextGenPMCore): NextGen PM Core object.
        batches_to_delete (list[dict]): List of dictionaries containing practice name and descriptions to delete.
        database (str): Database name. Options: "NGPROD" or "NGTEST". Defaults to "NGTEST".

    Example:
        batches_to_delete =[
            {
                "practice": "Proliance Southwest Seattle Orthopedics",
                "descriptions": [
                    "*****",
                    "******",
                    "******",
                ]
            },
            {
                "practice": "Proliance Hand Wrist & Elbow Physicians",
                "descriptions": [
                    "*******",
                    "*******",
                    "*****",
                ]
            }
        ]
    """
    report_list = []
    next_gen.login(practice="_Central Office", database=database)
    next_gen.desktop_app.click_no_button_in_next_gen_alert()
    for batches in batches_to_delete:

        logger.info(f"Selecting practice: {batches['practice']}")
        try:
            next_gen.select_practice_from_app(batches["practice"])
        except Exception as e:
            logger.warning(f"Error selecting practice {batches['practice']}. Error: {e}")
            next_gen.desktop_app.dialog.child_window(auto_id="cmdCancel").click()
            continue
        batch_deleter = BatchDeleter(next_gen, batches["descriptions"], batches["practice"])
        report = batch_deleter.delete()
        report_list.append(report)

    if next_gen_process := next_gen.desktop_app.get_app_session_if_running(next_gen.app_path):
        logger.debug("Closing the NextGen process.")
        next_gen.close_session(next_gen_process)
    return report_list


if __name__ == "__main__":
    batches_to_delete = [
        {
            "practice": "Proliance Southwest Seattle Orthopedics",
            "descriptions": ["*******", "*******", "********"],
        },
    ]
    next_gen = NextGenPMCore()
    delete_batches(next_gen, batches_to_delete)
