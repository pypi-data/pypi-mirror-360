"use client";

import { useState } from "react";
import { useTemplates, useTemplate } from "@/hooks";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Markdown from "react-markdown";
import { useRouter } from "next/navigation";
import remarkGfm from "remark-gfm";

export function TemplatesList() {
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const router = useRouter();

  // Query for all templates
  const {
    data: templates,
    isLoading: templatesLoading,
    error: templatesError
  } = useTemplates();

  // Query for selected template
  const {
    data: templateDetails,
    isLoading: templateLoading
  } = useTemplate(selectedTemplate || "");

  if (templatesLoading) {
    return <div className="p-4">Loading templates...</div>;
  }

  if (templatesError) {
    return <div className="p-4 text-red-500">Error loading templates</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Available Templates</h2>
        {templates?.map((template) => (
          <Card key={template.id} className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent
              className="p-4"
              onClick={() => setSelectedTemplate(template.id)}
            >
              <h3 className="font-medium">{template.name}</h3>
              {template.description && (
                <p className="text-sm text-gray-500">{template.description}</p>
              )}
              {/* TODO: Add a preview of the template */}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Template Details</h2>
        {selectedTemplate ? (
          templateLoading ? (
            <div>Loading template details...</div>
          ) : templateDetails ? (
            <Card>
              <CardContent className="p-4">
                <h3 className="font-medium">{templateDetails.name}</h3>
                {templateDetails.description && (
                  <Markdown remarkPlugins={[remarkGfm]}>{templateDetails.description}</Markdown>
                )}
                <div className="bg-gray-100 p-4 rounded-md">
                  <Markdown remarkPlugins={[remarkGfm]}>
                    {templateDetails.content}
                  </Markdown>
                </div>
                <div className="mt-4">
                  <Button onClick={() => router.push(`/templates/${templateDetails.id}`)}>Use This Template</Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div>No template selected</div>
          )
        ) : (
          <div className="text-gray-500">Select a template to view details</div>
        )}
      </div>
    </div>
  );
} 