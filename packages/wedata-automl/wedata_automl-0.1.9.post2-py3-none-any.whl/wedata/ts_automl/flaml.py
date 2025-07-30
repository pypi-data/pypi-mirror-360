from __future__ import annotations
import numpy as np
from flaml import AutoML
import mlflow
import os
import time
from typing import Union
from flaml.automl.logger import logger
from flaml.automl.spark import DataFrame, psDataFrame
from flaml.automl.state import AutoMLState
from flaml.automl.task.task import Task
from flaml.fabric.mlflow import MLflowIntegration

#
# def log_automl_patch(self, automl):
#     self.set_best_iter(automl)
#     if self.autolog:
#         if self.parent_run_id is not None:
#             mlflow.start_run(run_id=self.parent_run_id, experiment_id=self.experiment_id)
#             mlflow.log_metric("best_validation_loss", automl._state.best_loss)
#             mlflow.log_metric("best_iteration", automl._best_iteration)
#             mlflow.log_metric("num_child_runs", len(self.infos))
#             if automl._trained_estimator is not None and not self.has_model and automl._trained_estimator._model is not None:
#                 self.log_model(
#                     automl._trained_estimator._model, automl.best_estimator, signature=automl.estimator_signature
#                 )
#                 self.pickle_and_log_automl_artifacts(
#                     automl, automl.model, automl.best_estimator, signature=automl.pipeline_signature
#                 )
#                 self.has_model = True
#
#         self.adopt_children(automl)
#
#     if self.manual_log:
#         best_mlflow_run_id = self.manual_run_ids[automl._best_iteration]
#         best_run_name = self.mlflow_client.get_run(best_mlflow_run_id).info.run_name
#         automl.best_run_id = best_mlflow_run_id
#         automl.best_run_name = best_run_name
#         self.mlflow_client.set_tag(best_mlflow_run_id, "flaml.best_run", True)
#         self.best_run_id = best_mlflow_run_id
#         if self.parent_run_id is not None:
#             conf = automl._config_history[automl._best_iteration][1].copy()
#             if "ml" in conf.keys():
#                 conf = conf["ml"]
#
#             mlflow.log_params(conf)
#             mlflow.log_param("best_learner", automl._best_estimator)
#             if not self.has_summary:
#                 logger.info(f"logging best model {automl.best_estimator}")
#                 self.copy_mlflow_run(best_mlflow_run_id, self.parent_run_id)
#                 self.has_summary = True
#                 if automl._trained_estimator is not None and not self.has_model and automl._trained_estimator._model is not None:
#                     self.log_model(
#                         automl._trained_estimator._model,
#                         automl.best_estimator,
#                         signature=automl.estimator_signature,
#                     )
#                     self.pickle_and_log_automl_artifacts(
#                         automl, automl.model, automl.best_estimator, signature=automl.pipeline_signature
#                     )
#                     self.has_model = True
#
# MLflowIntegration.log_automl = log_automl_patch
#
# def search_patch(self):
#     # initialize the search_states
#     self._eci = []
#     self._state.best_loss = float("+inf")
#     self._state.time_from_start = 0
#     self._estimator_index = None
#     self._best_iteration = 0
#     self._time_taken_best_iter = 0
#     self._config_history = {}
#     self._max_iter_per_learner = 10000
#     self._iter_per_learner = {e: 0 for e in self.estimator_list}
#     self._iter_per_learner_fullsize = {e: 0 for e in self.estimator_list}
#     self._fullsize_reached = False
#     self._trained_estimator = None
#     self._best_estimator = None
#     self._retrained_config = {}
#     self._warn_threshold = 10
#     self._selected = None
#     self.modelcount = 0
#     if self._max_iter < 2 and self.estimator_list and self._state.retrain_final:
#         # when max_iter is 1, no need to search
#         self.modelcount = self._max_iter
#         self._max_iter = 0
#         self._best_estimator = estimator = self.estimator_list[0]
#         self._selected = state = self._search_states[estimator]
#         state.best_config_sample_size = self._state.data_size[0]
#         state.best_config = state.init_config[0] if state.init_config else {}
#     elif self._use_ray is False and self._use_spark is False:
#         self._search_sequential()
#     else:
#         self._search_parallel()
#     # Add a checkpoint for the current best config to the log.
#     if self._training_log:
#         self._training_log.checkpoint()
#     self._state.time_from_start = time.time() - self._start_time_flag
#     if self._best_estimator:
#         if self.mlflow_integration:
#             self.mlflow_integration.log_automl(self)
#             if mlflow.active_run() is None:
#                 if self.mlflow_integration.parent_run_id is not None and self.mlflow_integration.autolog:
#                     # ensure result of retrain autolog to parent run
#                     mlflow.start_run(run_id=self.mlflow_integration.parent_run_id)
#         self._selected = self._search_states[self._best_estimator]
#         self.modelcount = sum(search_state.total_iter for search_state in self._search_states.values())
#         if self._trained_estimator:
#             logger.info(f"selected model: {self._trained_estimator.model}")
#         estimators = []
#         if self._ensemble and self._state.task in (
#                 "binary",
#                 "multiclass",
#                 "regression",
#         ):
#             search_states = list(x for x in self._search_states.items() if x[1].best_config)
#             search_states.sort(key=lambda x: x[1].best_loss)
#             estimators = [
#                 (
#                     x[0],
#                     x[1].learner_class(
#                         task=self._state.task,
#                         n_jobs=self._state.n_jobs,
#                         **AutoMLState.sanitize(x[1].best_config),
#                     ),
#                 )
#                 for x in search_states[:2]
#             ]
#             estimators += [
#                 (
#                     x[0],
#                     x[1].learner_class(
#                         task=self._state.task,
#                         n_jobs=self._state.n_jobs,
#                         **AutoMLState.sanitize(x[1].best_config),
#                     ),
#                 )
#                 for x in search_states[2:]
#                 if x[1].best_loss < 4 * self._selected.best_loss
#             ]
#             logger.info([(estimator[0], estimator[1].params) for estimator in estimators])
#         if len(estimators) > 1:
#             if self._state.task.is_classification():
#                 from sklearn.ensemble import StackingClassifier as Stacker
#             else:
#                 from sklearn.ensemble import StackingRegressor as Stacker
#             if self._use_ray is not False:
#                 import ray
#
#                 n_cpus = ray.is_initialized() and ray.available_resources()["CPU"] or os.cpu_count()
#             elif self._use_spark:
#                 from flaml.tune.spark.utils import get_n_cpus
#
#                 n_cpus = get_n_cpus()
#             else:
#                 n_cpus = os.cpu_count()
#             ensemble_n_jobs = (
#                 -self._state.n_jobs  # maximize total parallelization degree
#                 if abs(self._state.n_jobs) == 1  # 1 and -1 correspond to min/max parallelization
#                 else max(1, int(n_cpus / 2 / self._state.n_jobs))
#                 # the total degree of parallelization = parallelization degree per estimator * parallelization degree of ensemble
#             )
#             if isinstance(self._ensemble, dict):
#                 final_estimator = self._ensemble.get("final_estimator", self._trained_estimator)
#                 passthrough = self._ensemble.get("passthrough", True)
#                 ensemble_n_jobs = self._ensemble.get("n_jobs", ensemble_n_jobs)
#             else:
#                 final_estimator = self._trained_estimator
#                 passthrough = True
#             stacker = Stacker(
#                 estimators,
#                 final_estimator,
#                 n_jobs=ensemble_n_jobs,
#                 passthrough=passthrough,
#             )
#             sample_weight_dict = (
#                     (self._sample_weight_full is not None) and {"sample_weight": self._sample_weight_full} or {}
#             )
#             for e in estimators:
#                 e[1].__class__.init()
#             import joblib
#
#             try:
#                 logger.info("Building ensemble with tuned estimators")
#                 stacker.fit(
#                     self._X_train_all,
#                     self._y_train_all,
#                     **sample_weight_dict,  # NOTE: _search is after kwargs is updated to fit_kwargs_by_estimator
#                 )
#                 logger.info(f"ensemble: {stacker}")
#                 self._trained_estimator = stacker
#                 self._trained_estimator.model = stacker
#             except ValueError as e:
#                 if passthrough:
#                     logger.warning(
#                         "Using passthrough=False for ensemble because the data contain categorical features."
#                     )
#                     stacker = Stacker(
#                         estimators,
#                         final_estimator,
#                         n_jobs=self._state.n_jobs,
#                         passthrough=False,
#                     )
#                     stacker.fit(
#                         self._X_train_all,
#                         self._y_train_all,
#                         **sample_weight_dict,  # NOTE: _search is after kwargs is updated to fit_kwargs_by_estimator
#                     )
#                     logger.info(f"ensemble: {stacker}")
#                     self._trained_estimator = stacker
#                     self._trained_estimator.model = stacker
#                 else:
#                     raise e
#             except joblib.externals.loky.process_executor.TerminatedWorkerError:
#                 logger.error(
#                     "No enough memory to build the ensemble."
#                     " Please try increasing available RAM, decreasing n_jobs for ensemble, or disabling ensemble."
#                 )
#         elif self._state.retrain_final:
#             # reset time budget for retraining
#             if self._max_iter > 1:
#                 self._state.time_budget = -1
#             if (
#                     self._state.task.is_ts_forecast()
#                     or self._trained_estimator is None
#                     or self._trained_estimator.model is None
#                     or (
#                     self._state.time_budget < 0
#                     or self._state.time_budget - self._state.time_from_start
#                     > self._selected.est_retrain_time(self.data_size_full)
#             )
#                     and self._selected.best_config_sample_size == self._state.data_size[0]
#             ):
#                 state = self._search_states[self._best_estimator]
#                 (
#                     self._trained_estimator,
#                     retrain_time,
#                 ) = self._state._train_with_config(
#                     self._best_estimator,
#                     state.best_config,
#                     self.data_size_full,
#                     is_retrain=True,
#                 )
#                 logger.info(f"retrain {self._best_estimator} for {retrain_time:.1f}s")
#                 state.best_config_train_time = retrain_time
#                 if self._trained_estimator:
#                     logger.info(f"retrained model: {self._trained_estimator.model}")
#                     if self.best_run_id is not None:
#                         logger.info(f"Best MLflow run name: {self.best_run_name}")
#                         logger.info(f"Best MLflow run id: {self.best_run_id}")
#                     if self.mlflow_integration is not None:
#                         # try log retrained model
#                         if all(
#                                 [
#                                     self.mlflow_integration.manual_log,
#                                     not self.mlflow_integration.has_model,
#                                     self.mlflow_integration.parent_run_id is not None,
#                                 ]
#                         ):
#                             if mlflow.active_run() is None:
#                                 mlflow.start_run(run_id=self.mlflow_integration.parent_run_id)
#                             self.mlflow_integration.log_model(
#                                 self._trained_estimator.model,
#                                 self.best_estimator,
#                                 signature=self.estimator_signature,
#                             )
#                             self.mlflow_integration.pickle_and_log_automl_artifacts(
#                                 self, self.model, self.best_estimator, signature=self.pipeline_signature
#                             )
#             else:
#                 logger.info("not retraining because the time budget is too small.")
#
#
# AutoML._search = search_patch

class WeDataTimeSeriesAutoML:

    def __init__(self, **settings):

        self.aml = AutoML(automl_settings=settings)


    def fit(self,
            X_train=None,
            y_train=None,
            dataframe=None,
            label=None,
            metric=None,
            task: Union[str, Task, None] = None,
            n_jobs=None,
            # gpu_per_trial=0,
            log_file_name=None,
            estimator_list=None,
            time_budget=None,
            max_iter=None,
            sample=None,
            ensemble=None,
            eval_method=None,
            log_type=None,
            model_history=None,
            split_ratio=None,
            n_splits=None,
            log_training_metric=None,
            mem_thres=None,
            pred_time_limit=None,
            train_time_limit=None,
            X_val=None,
            y_val=None,
            sample_weight_val=None,
            groups_val=None,
            groups=None,
            verbose=None,
            retrain_full=None,
            split_type=None,
            learner_selector=None,
            hpo_method=None,
            starting_points=None,
            seed=None,
            n_concurrent_trials=None,
            keep_search_state=None,
            preserve_checkpoint=True,
            early_stop=None,
            force_cancel=None,
            append_log=None,
            auto_augment=None,
            min_sample_size=None,
            use_spark=None,
            free_mem_ratio=0,
            metric_constraints=None,
            custom_hp=None,
            time_col=None,
            cv_score_agg_func=None,
            skip_transform=None,
            fit_kwargs_by_estimator=None,
            mlflow_exp_name=None,
            mlflow_run_name=None,
            **fit_kwargs,
            ):
        if mlflow_exp_name is None:
            mlflow_exp_name = "Default"
        mlflow.set_experiment(mlflow_exp_name)
        with mlflow.start_run(run_name=mlflow_run_name) as run:
            self.aml.fit(
                X_train=X_train,
                y_train=y_train,
                dataframe=dataframe,
                label=label,
                metric=metric,
                task=task,
                n_jobs=n_jobs,
                # gpu_per_trial=0,
                log_file_name=log_file_name,
                estimator_list=estimator_list,
                time_budget=time_budget,
                max_iter=max_iter,
                sample=sample,
                ensemble=ensemble,
                eval_method=eval_method,
                log_type=log_type,
                model_history=model_history,
                split_ratio=split_ratio,
                n_splits=n_splits,
                log_training_metric=log_training_metric,
                mem_thres=mem_thres,
                pred_time_limit=pred_time_limit,
                train_time_limit=train_time_limit,
                X_val=X_val,
                y_val=y_val,
                sample_weight_val=sample_weight_val,
                groups_val=groups_val,
                groups=groups,
                verbose=verbose,
                retrain_full=retrain_full,
                split_type=split_type,
                learner_selector=learner_selector,
                hpo_method=hpo_method,
                starting_points=starting_points,
                seed=seed,
                n_concurrent_trials=n_concurrent_trials,
                keep_search_state=keep_search_state,
                preserve_checkpoint=preserve_checkpoint,
                early_stop=early_stop,
                force_cancel=force_cancel,
                append_log=append_log,
                auto_augment=auto_augment,
                min_sample_size=min_sample_size,
                use_ray=None,
                use_spark=use_spark,
                free_mem_ratio=free_mem_ratio,
                metric_constraints=metric_constraints,
                custom_hp=custom_hp,
                time_col=time_col,
                cv_score_agg_func=cv_score_agg_func,
                skip_transform=skip_transform,
                mlflow_logging=True,
                fit_kwargs_by_estimator=fit_kwargs_by_estimator,
                mlflow_exp_name=mlflow_exp_name,
                **fit_kwargs
            )

    def predict(
            self,
            X: Union[np.array, DataFrame, list[str], list[list[str]], psDataFrame],
            **pred_kwargs,
    ):
        self.aml.predict(X, **pred_kwargs)

