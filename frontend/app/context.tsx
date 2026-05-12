import React, { useContext } from "react";
import { SystemManager } from "generated";

export const SystemContext = React.createContext<SystemManager | null>(null);
export function useSystemContext() {
    return useContext(SystemContext)
}