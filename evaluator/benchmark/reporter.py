from os.path import dirname, abspath, join

from evaluator.benchmark.definitions import CaseStatuses

from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    CompositeKey,
    IntegrityError,
    SqliteDatabase,
)

import time


def get_unique_id():
    return str(time.time()).replace(".", "_")


def create_database_client():
    DATABASE_PATH = join(dirname(dirname(abspath(__file__))), "data")
    DATABASE = SqliteDatabase(join(DATABASE_PATH, "reports_" + get_unique_id() + ".db"))

    class ManagerReport(Model):
        benchmark_id = CharField(primary_key=True)
        case_set_id = CharField()
        total_cases = IntegerField()
        current_case_index = IntegerField()
        current_case_id = CharField(null=True)

        class Meta:
            database = DATABASE
            only_save_dirty = True

    class AIReport(Model):
        manager_report = ForeignKeyField(ManagerReport, backref="ai_reports")
        ai_name = CharField()
        case_id = CharField()
        healthcheck_status = IntegerField(choices=[(-1, -1), (0, 0), (1, 1)])
        case_status = IntegerField(choices=[(-1, -1), (0, 0), (1, 1)])
        health_checks = IntegerField()
        errors = IntegerField()
        soft_timeouts = IntegerField()
        hard_timeouts = IntegerField()

        class Meta:
            database = DATABASE
            only_save_dirty = True
            primary_key = CompositeKey("manager_report", "ai_name", "case_id")

    class DatabaseClient:
        def __init__(self):
            self.database = DATABASE
            self.connection = self.database.connect(reuse_if_open=True)
            self.database.create_tables([ManagerReport, AIReport])

        def shutdown(self):
            self.database.stop()
            self.connection.close()

        def create_manager_report(self, benchmark_id, case_set_id, total_cases):
            with self.database:
                try:
                    report = ManagerReport.create(
                        benchmark_id=benchmark_id,
                        case_set_id=case_set_id,
                        total_cases=total_cases,
                        current_case_index=-1,
                        current_case_id=None,
                    )
                except IntegrityError:
                    report = self.select_manager_report(benchmark_id)

            return report

        def select_manager_report(self, benchmark_id, prefetch=False):
            with self.database:
                query = ManagerReport.select().where(
                    ManagerReport.benchmark_id == benchmark_id
                )
                if prefetch:
                    try:
                        report = query.prefetch(AIReport)[0]
                    except IndexError:
                        report = None
                else:
                    try:
                        report = query.get()
                    except ManagerReport.DoesNotExist:
                        report = None

            return report

        def delete_manager_report(self, report_instance=None, benchmark_id=None):
            with self.database:
                if report_instance and isinstance(report_instance, ManagerReport):
                    report_instance.delete_instance()
                    return True
                elif benchmark_id:
                    deleted = (
                        ManagerReport.select()
                        .where(ManagerReport.benchmark_id == benchmark_id)
                        .execute()
                    )
                    if deleted:
                        return True

            return False

        def update_manager_report(
            self,
            current_case_index,
            current_case_id,
            report_instance=None,
            benchmark_id=None,
        ):
            with self.database:
                if report_instance and isinstance(report_instance, ManagerReport):
                    report_instance.current_case_index = current_case_index
                    report_instance.current_case_id = current_case_id
                    report_instance.save()
                elif benchmark_id:
                    ManagerReport.update(
                        {
                            ManagerReport.current_case_index: current_case_index,
                            ManagerReport.current_case_id: current_case_id,
                        }
                    ).where(ManagerReport.benchmark_id == benchmark_id).execute()
                    report_instance = self.select_manager_report(
                        benchmark_id=benchmark_id
                    )
                else:
                    report_instance = None

            return report_instance

        def create_ai_report(self, manager_report, ai_name, case_id, data):
            if data["errors"]:
                case_status = int(CaseStatuses.ERROR)
            else:
                case_status = int(CaseStatuses.RUNNING)

            with self.database:
                try:
                    AIReport.create(
                        manager_report=manager_report,
                        ai_name=ai_name,
                        case_id=case_id,
                        healthcheck_status=data["healthcheck_status"],
                        case_status=case_status,
                        health_checks=data["health_checks"],
                        errors=data["errors"],
                        soft_timeouts=data["soft_timeouts"],
                        hard_timeouts=data["hard_timeouts"],
                    )
                except IntegrityError:
                    self.update_ai_report(
                        manager_report,
                        ai_name,
                        case_id,
                        error=data["errors"],
                        healthcheck_status=data["healthcheck_status"],
                        case_status=case_status,
                        health_checks=data["health_checks"],
                        soft_timeout=data["soft_timeouts"],
                        hard_timeout=data["hard_timeouts"],
                    )

        def select_ai_report(self, manager_report, ai_name, case_id):
            with self.database:
                query = AIReport.select().where(
                    AIReport.manager_report == manager_report,
                    AIReport.ai_name == ai_name,
                    AIReport.case_id == case_id,
                )
                try:
                    report = query.get()
                except AIReport.DoesNotExist:
                    report = None

            return report

        def delete_ai_report(
            self, report_instance=None, manager_report=None, ai_name=None, case_id=None
        ):
            with self.database:
                if report_instance and isinstance(report_instance, AIReport):
                    report_instance.delete_instance()
                    return True
                elif manager_report and ai_name and case_id:
                    deleted = (
                        AIReport.select()
                        .where(
                            AIReport.manager_report == manager_report,
                            AIReport.ai_name == ai_name,
                            AIReport.case_id == case_id,
                        )
                        .execute()
                    )
                    if deleted:
                        return True

            return False

        def update_ai_report(
            self,
            manager_report,
            ai_name,
            case_id,
            case_status,
            healthcheck_status=None,
            error=None,
            health_checks=False,
            soft_timeout=False,
            hard_timeout=False,
        ):
            with self.database:
                update_dict = {}

                update_dict[AIReport.case_status] = case_status

                if healthcheck_status is not None:
                    update_dict[AIReport.healthcheck_status] = healthcheck_status

                if error:
                    update_dict[AIReport.errors] = AIReport.errors + 1

                if health_checks:
                    update_dict[AIReport.health_checks] = AIReport.health_checks + 1

                if soft_timeout:
                    update_dict[AIReport.soft_timeouts] = AIReport.soft_timeouts + 1

                if hard_timeout:
                    update_dict[AIReport.hard_timeouts] = AIReport.hard_timeouts + 1

                query = AIReport.update(update_dict).where(
                    AIReport.manager_report == manager_report,
                    AIReport.ai_name == ai_name,
                    AIReport.case_id == case_id,
                )

                query.execute()

    return DatabaseClient
