"use client";

import type React from "react";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, Upload, FolderOpen } from "lucide-react";
import { apiService } from "@/lib/api";
import { useDragDrop } from "@/components/drag-drop-context";

interface CreateDatasetModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateDatasetModal({
  open,
  onOpenChange,
  onSuccess,
}: CreateDatasetModalProps) {
  const { toast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const {
    isDragging,
    activeDropZone,
    handleDragEnter,
    handleDragLeave,
    handleDragOver,
    handleDrop: contextHandleDrop,
  } = useDragDrop();

  const handleFileDrop = (e: React.DragEvent) => {
    contextHandleDrop(e, "create-dataset", (droppedFile) => {
      setFile(droppedFile);
      // Auto-fill name from file
      const fileName = droppedFile.name.replace(/\.[^/.]+$/, "");
      setName(fileName);
    });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      setFile(selectedFiles[0]);

      // Auto-fill name from first file or folder
      const firstFile = selectedFiles[0];
      if (firstFile.webkitRelativePath) {
        // Extract folder name from path
        const folderName = firstFile.webkitRelativePath.split("/")[0];
        setName(folderName);
      } else {
        // Use file name without extension
        const fileName = firstFile.name.replace(/\.[^/.]+$/, "");
        setName(fileName);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a file");
      return;
    }

    if (!name.trim()) {
      setError("Please enter a dataset name");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();

      // Add the file to FormData
      formData.append("dataset", file);
      formData.append("name", name.trim());
      formData.append("description", description.trim() || "");

      const result = await apiService.createDataset(formData);

      if (result.success) {
        onSuccess();
        resetForm();
        onOpenChange(false);
        toast({
          title: "Success",
          description: result.message,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create dataset");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setName("");
    setDescription("");
    setError("");
    setLoading(false);
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && !loading) {
      resetForm();
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        className="sm:max-w-md"
        onDragEnter={(e) => handleDragEnter(e, "create-dataset")}
        onDragLeave={(e) => handleDragLeave(e, "create-dataset")}
        onDragOver={(e) => handleDragOver(e, "create-dataset")}
        onDrop={handleFileDrop}
      >
        <DialogHeader>
          <DialogTitle>Create New Dataset</DialogTitle>
          <DialogDescription>
            Get started by uploading your dataset file.
          </DialogDescription>
        </DialogHeader>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
          onDragEnter={(e) => handleDragEnter(e, "create-dataset")}
          onDragLeave={(e) => handleDragLeave(e, "create-dataset")}
          onDragOver={(e) => handleDragOver(e, "create-dataset")}
          onDrop={handleFileDrop}
        >
          <div className="space-y-2">
            <Label htmlFor="dataset-file">Dataset File *</Label>
            <div
              className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                activeDropZone === "create-dataset" && isDragging
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-muted-foreground/50"
              }`}
            >
              <input
                id="dataset-file"
                type="file"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="dataset-file" className="block cursor-pointer">
                <div className="space-y-2">
                  <FolderOpen className="mx-auto h-8 w-8 text-muted-foreground" />
                  <div className="text-sm">
                    <span className="font-medium text-primary hover:underline">
                      {activeDropZone === "create-dataset" && isDragging
                        ? "Drop your file here"
                        : "Drop your file here or click to select"}
                    </span>
                    <p className="text-muted-foreground mt-1">
                      Choose your dataset file
                    </p>
                  </div>
                </div>
              </label>
            </div>
            {file && (
              <p className="text-sm text-muted-foreground">
                Selected: {file.name}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="name">Dataset Name *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter dataset name"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description (optional)</Label>
            <Input
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the dataset"
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription className="break-all">{error}</AlertDescription>
            </Alert>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Create Dataset
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
