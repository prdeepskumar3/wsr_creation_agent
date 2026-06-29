export type ApiResponse<TData> = {
  data: TData;
  meta: {
    correlationId: string;
    version: string;
  };
  errors: Array<{ code: string; message: string; field?: string }>;
};

