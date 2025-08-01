import { useMutation } from "@tanstack/react-query";
import { client } from "../../api/client";
import { queryClient } from "../../main";

const importFamilyMembers = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  return client.post<{
    data: {
      success: Array<{
        row: number;
        family_member_id: number;
        paciente_nombre: string;
        familiar_nombre: string;
        parentesco: string;
        es_acudiente: boolean;
      }>;
      errors: Array<{
        row: number;
        error: string;
      }>;
      total_processed: number;
      total_success: number;
      total_errors: number;
    };
    message: string;
  }>("/api/family-members/import/excel", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const useImportFamilyMembers = () => {
  return useMutation({
    mutationKey: ["import-family-members"],
    mutationFn: importFamilyMembers,
    onSuccess: () => {
      // Invalidar todas las queries relacionadas con familiares
      queryClient.invalidateQueries({ queryKey: ["get-user"] });
      queryClient.invalidateQueries({
        predicate: (query) =>
          query.queryKey[0] === "get-user" ||
          query.queryKey[0] === "get-user-family-members",
      });
    },
  });
};
