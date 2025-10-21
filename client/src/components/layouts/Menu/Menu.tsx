import { AppSidebar } from "@/components/layouts/Menu/app-sidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import type { ReactNode } from "react";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

export default function Menu({ children }: { children: ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="bg-red-600 flex flex-col transition-[margin] mt-16 group-has-data-[collapsible=icon]/sidebar-wrapper:mt-12">
        <header
          className={cn(
            "flex border-b h-16 shrink-0 items-center gap-2 transition-[width,height,transform] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12",
            "bg-white w-full fixed top-0"
          )}
        >
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <p className="font-medium">Chatbot bovino</p>
          </div>
        </header>
          <main className="flex w-full min-h-full bg-gray-100 overflow-y-auto">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
