import { ArrowRight, FileText, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react"

export default function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8 py-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Good morning, Officer</h1>
          <p className="mt-1 text-sm text-slate-500">Here's a digest of your recent corporate lending pipeline.</p>
        </div>
        <div className="mt-4 md:mt-0 flex">
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            Start New Assessment
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {/* Stat Card 1 */}
        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-6 w-6 text-slate-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-slate-500 truncate">Pending CAMs</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-slate-900">12</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 px-5 py-3 border-t border-slate-200">
            <div className="text-sm">
              <a href="#" className="font-medium text-blue-600 hover:text-blue-500">View all</a>
            </div>
          </div>
        </div>

        {/* Stat Card 2 */}
        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-6 w-6 text-green-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-slate-500 truncate">Approved This Week</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-slate-900">4</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 px-5 py-3 border-t border-slate-200">
            <div className="text-sm">
              <a href="#" className="font-medium text-blue-600 hover:text-blue-500">View all</a>
            </div>
          </div>
        </div>

        {/* Stat Card 3 */}
        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <AlertTriangle className="h-6 w-6 text-yellow-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-slate-500 truncate">High Risk Alerts</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-red-600">2</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 px-5 py-3 border-t border-slate-200">
            <div className="text-sm">
              <a href="#" className="font-medium text-blue-600 hover:text-blue-500">Review alerts</a>
            </div>
          </div>
        </div>

        {/* Stat Card 4 */}
        <div className="bg-white overflow-hidden shadow-sm rounded-lg border border-slate-200">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-6 w-6 text-blue-400" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-slate-500 truncate">Total Disbursed Limit</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-slate-900">₹850 Cr</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-slate-50 px-5 py-3 border-t border-slate-200">
            <div className="text-sm">
              <a href="#" className="font-medium text-blue-600 hover:text-blue-500">View portfolio</a>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Recent Applications List */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-slate-200">
          <div className="px-6 py-5 border-b border-slate-200 flex justify-between items-center">
            <h3 className="text-lg leading-6 font-medium text-slate-900">Recent Applications</h3>
            <button className="text-sm text-blue-600 font-medium hover:text-blue-700">See all</button>
          </div>
          <ul className="divide-y divide-slate-200">
            {/* Applicant 1 */}
            <li>
              <a href="#" className="block hover:bg-slate-50 transition-colors">
                <div className="px-6 py-4 flex items-center">
                  <div className="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between">
                    <div className="truncate">
                      <div className="flex text-sm">
                        <p className="font-medium text-blue-600 truncate">TechVision Global Pvt Ltd</p>
                        <p className="ml-1 flex-shrink-0 font-normal text-slate-500">in IT Consulting</p>
                      </div>
                      <div className="mt-2 flex">
                        <div className="flex items-center text-sm text-slate-500">
                          <CheckCircle className="flex-shrink-0 mr-1.5 h-4 w-4 text-green-400" />
                          <p>
                            AI Pre-screening <span className="font-medium text-slate-900">Complete</span>
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 flex-shrink-0 sm:mt-0 sm:ml-5">
                      <div className="flex -space-x-1 overflow-hidden">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          Review CAM
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="ml-5 flex-shrink-0">
                    <ArrowRight className="h-5 w-5 text-slate-400" />
                  </div>
                </div>
              </a>
            </li>
            
            {/* Applicant 2 */}
            <li>
              <a href="#" className="block hover:bg-slate-50 transition-colors">
                <div className="px-6 py-4 flex items-center">
                  <div className="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between">
                    <div className="truncate">
                      <div className="flex text-sm">
                        <p className="font-medium text-slate-900 truncate">Apex Manufacturing Ltd</p>
                        <p className="ml-1 flex-shrink-0 font-normal text-slate-500">in Industrials</p>
                      </div>
                      <div className="mt-2 flex">
                        <div className="flex items-center text-sm text-slate-500">
                          <AlertTriangle className="flex-shrink-0 mr-1.5 h-4 w-4 text-yellow-400" />
                          <p>
                            Needs details: <span className="font-medium text-slate-900">GSTR-3B Mismatch</span>
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 flex-shrink-0 sm:mt-0 sm:ml-5">
                      <div className="flex -space-x-1 overflow-hidden">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          Pending Info
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="ml-5 flex-shrink-0">
                    <ArrowRight className="h-5 w-5 text-slate-400" />
                  </div>
                </div>
              </a>
            </li>
          </ul>
        </div>

        {/* Intelligence feed */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200">
          <div className="px-6 py-5 border-b border-slate-200">
            <h3 className="text-lg leading-6 font-medium text-slate-900">Agent Intelligence Alerts</h3>
          </div>
          <div className="px-6 py-5 space-y-6">
            <div className="relative">
              <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-slate-200" aria-hidden="true"></span>
              <ul className="space-y-4">
                <li className="relative">
                  <div className="relative flex items-start space-x-3">
                    <div className="relative">
                      <span className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center ring-8 ring-white">
                        <AlertTriangle className="h-4 w-4 text-red-600" aria-hidden="true" />
                      </span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div>
                        <div className="text-sm">
                          <a href="#" className="font-medium text-slate-900">Data Paradox detected</a>
                        </div>
                        <p className="mt-0.5 text-xs text-slate-500">2 hrs ago</p>
                      </div>
                      <div className="mt-2 text-sm text-slate-700">
                        <p>Circular trading suspected for <strong>Zenith Metals</strong> based on recent bank statement parsing vs GST filings.</p>
                      </div>
                    </div>
                  </div>
                </li>
                
                <li className="relative">
                  <div className="relative flex items-start space-x-3">
                    <div className="relative">
                      <span className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center ring-8 ring-white">
                        <TrendingUp className="h-4 w-4 text-blue-600" aria-hidden="true" />
                      </span>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div>
                        <div className="text-sm">
                          <a href="#" className="font-medium text-slate-900">Sector Headwinds Adjusted</a>
                        </div>
                        <p className="mt-0.5 text-xs text-slate-500">5 hrs ago</p>
                      </div>
                      <div className="mt-2 text-sm text-slate-700">
                        <p>Research Agent updated risk models based on latest RBI regulations for NBFCs.</p>
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
            
            <div className="pt-4 border-t border-slate-200">
              <button className="w-full flex items-center justify-center px-4 py-2 border border-slate-300 shadow-sm text-sm font-medium rounded-md text-slate-700 bg-white hover:bg-slate-50">
                View All Intelligence
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
