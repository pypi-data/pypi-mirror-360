import h2o.automl
import mlflow
from pysparkling import H2OContext
from pyspark.sql import SparkSession




class WeDataH2oAutoML:
    """
    H2O AutoML implementation. Integrate Mlflow Autolog.

    参数说明见 init fit 方法。
    """

    def __init__(self,
                 nfolds=-1,
                 balance_classes=False,
                 class_sampling_factors=None,
                 max_after_balance_size=5.0,
                 max_runtime_secs=None,
                 max_runtime_secs_per_model=None,
                 max_models=None,
                 distribution="AUTO",
                 stopping_metric="AUTO",
                 stopping_tolerance=None,
                 stopping_rounds=3,
                 seed=None,
                 project_name=None,
                 exclude_algos=None,
                 include_algos=None,
                 exploitation_ratio=-1,
                 modeling_plan=None,
                 preprocessing=None,
                 monotone_constraints=None,
                 keep_cross_validation_predictions=False,
                 keep_cross_validation_models=False,
                 keep_cross_validation_fold_assignment=False,
                 sort_metric="AUTO",
                 custom_metric_func=None,
                 export_checkpoints_dir=None,
                 verbosity="warn",
                 **kwargs):

        self.leaderboard = None
        self.nfolds = nfolds
        self.balance_classes = balance_classes
        self.class_sampling_factors = class_sampling_factors
        self.max_after_balance_size = max_after_balance_size
        self.max_runtime_secs = max_runtime_secs
        self.max_runtime_secs_per_model = max_runtime_secs_per_model
        self.max_models = max_models
        self.distribution = distribution
        self.stopping_metric = stopping_metric
        self.stopping_tolerance = stopping_tolerance
        self.stopping_rounds = stopping_rounds
        self.seed = seed
        self.project_name = project_name
        self.exclude_algos = exclude_algos
        self.include_algos = include_algos
        self.exploitation_ratio = exploitation_ratio
        self.modeling_plan = modeling_plan
        self.preprocessing = preprocessing
        self.monotone_constraints = monotone_constraints
        self.keep_cross_validation_predictions = keep_cross_validation_predictions
        self.keep_cross_validation_models = keep_cross_validation_models
        self.keep_cross_validation_fold_assignment = keep_cross_validation_fold_assignment
        self.sort_metric = sort_metric
        self.custom_metric_func = custom_metric_func
        self.export_checkpoints_dir = export_checkpoints_dir
        self.verbosity = verbosity
        # 获取当前 SparkSession
        spark = SparkSession.builder.getOrCreate()
        #关闭spark cosn ranger TODO 在增加了cosn-ranger-interface.jar 包后要删除下面代码
        spark.conf.set("spark.hadoop.fs.cosn.ranger.enable", "false")


        self.hc = H2OContext.getOrCreate()


        self.aml = h2o.automl.H2OAutoML(
            nfolds=self.nfolds,
            balance_classes=self.balance_classes,
            class_sampling_factors=self.class_sampling_factors,
            max_after_balance_size=self.max_after_balance_size,
            max_runtime_secs=self.max_runtime_secs,
            max_runtime_secs_per_model=self.max_runtime_secs_per_model,
            max_models=self.max_models,
            distribution=self.distribution,
            stopping_metric=self.stopping_metric,
            stopping_tolerance=self.stopping_tolerance,
            stopping_rounds=self.stopping_rounds,
            seed=self.seed,
            project_name=self.project_name,
            exclude_algos=self.exclude_algos,
            include_algos=self.include_algos,
            exploitation_ratio=self.exploitation_ratio,
            modeling_plan=self.modeling_plan,
            preprocessing=self.preprocessing,
            monotone_constraints=self.monotone_constraints,
            keep_cross_validation_predictions=self.keep_cross_validation_predictions,
            keep_cross_validation_models=self.keep_cross_validation_models,
            keep_cross_validation_fold_assignment=self.keep_cross_validation_fold_assignment,
            sort_metric=self.sort_metric,
            custom_metric_func=self.custom_metric_func,
            export_checkpoints_dir=self.export_checkpoints_dir,
            verbosity=self.verbosity
        )

    def train(self, x=None, y=None, training_frame=None, fold_column=None,
              weights_column=None, validation_frame=None, leaderboard_frame=None, blending_frame=None, mlflow_experiment_name=None, mlflow_run_name=None):
        if mlflow_experiment_name is not None:
            mlflow.set_experiment(mlflow_experiment_name)
        training_frame = self.hc.asH2OFrame(training_frame)
        self.aml.train(x, y, training_frame, fold_column, weights_column, validation_frame, leaderboard_frame, blending_frame)

        self.leaderboard = self.aml.leaderboard
        leaderboard = self.leaderboard.as_data_frame()
        input_example_h2o_frame = training_frame.head(5) if training_frame.nrows > 5 else x

        input_example = input_example_h2o_frame.as_data_frame()
        output_example_h2o_frame = self.aml.get_best_model().predict(input_example_h2o_frame)
        output_example = output_example_h2o_frame.as_data_frame()
        # 获取所有模型ID
        model_ids = list(self.aml.leaderboard['model_id'].as_data_frame().iloc[:, 0])
        with mlflow.start_run(run_name=mlflow_run_name):
            # 保存最佳模型
            best_model = self.aml.get_best_model()
            signature = mlflow.models.signature.infer_signature(input_example, output_example)
            mlflow.h2o.log_model(best_model, "best_model", signature=signature)
            # 记录模型参数
            params = {k: str(v['actual']) for k, v in best_model.params.items()}
            mlflow.log_param("model_name", best_model.model_id)
            mlflow.log_params(params)
            # 从 leaderboard 里取出该模型的所有 metric
            row = leaderboard[leaderboard['model_id'] == best_model.model_id].iloc[0]
            # 去掉 model_id 列，只保留 metric
            metrics = row.drop('model_id').to_dict()
            # 转换为 float，避免有些是 numpy 类型
            metrics = {"best_"+k: float(v) for k, v in metrics.items()}
            mlflow.log_metrics(metrics)

            for mid in model_ids:
                with mlflow.start_run(run_name=mid, nested=True):
                    model = h2o.get_model(mid)
                    mlflow.h2o.log_model(model, "model", signature=signature)
                    mlflow.log_param("model_name", mid)

                    # 记录模型参数
                    params = {k: str(v['actual']) for k, v in model.params.items()}
                    mlflow.log_params(params)

                    # 从 leaderboard 里取出该模型的所有 metric
                    row = leaderboard[leaderboard['model_id'] == mid].iloc[0]
                    # 去掉 model_id 列，只保留 metric
                    metrics = row.drop('model_id').to_dict()
                    # 转换为 float，避免有些是 numpy 类型
                    metrics = {k: float(v) for k, v in metrics.items()}
                    mlflow.log_metrics(metrics)


    def predict(self, test_data):
        test_data = self.hc.asH2OFrame(test_data)
        self.aml.predict(test_data)